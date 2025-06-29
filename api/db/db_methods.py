# A file for database methods for querrying and manipulating the database.
from datetime import datetime
from sqlalchemy import Subquery, select, func, and_, or_, sql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from werkzeug.datastructures import MultiDict
from enum import Enum
import uuid

try:
    from db.models import Metadata, Benchmark, Department, Result, Hostname, \
        DepartmentUser, BearerToken
    from db.db import db
except ImportError:
    from .models import Metadata, Benchmark, Department, Result, Hostname, \
        DepartmentUser, BearerToken
    from .db import db


class Filter_type(Enum):
    STANDARD = 1
    MINMAXTIME = 2
    OTHER = 3


def get_metadata(user_handle: str,
                 is_super_admin: bool,
                 args: MultiDict[str, str],
                 ids: bool = False) -> dict | list[str]:
    """Converting from arguments in request.args to function arguments."""
    return execute_query(
        user_handle,
        is_super_admin,
        min_time=datetime.fromisoformat(args.get('min_time'))
        if args.get('min_time') else None,
        max_time=datetime.fromisoformat(args.get('max_time'))
        if args.get('max_time') else None,
        departments=args.getlist('department'),
        benchmarks=args.getlist('benchmark'),
        results=args.getlist('result'),
        hostnames=args.getlist('hostname'),
        search_string=args.get('search', type=str),
        page=args.get('page', 0, type=int),
        page_size=args.get('page_size', 20, type=int),
        ids_only=ids
    )


def get_benchmark(name: str) -> Benchmark:
    """Retrieve a benchmark by name, or create it if it does not exist."""
    stmt = select(Benchmark).where(Benchmark.name == name)
    benchmark = db.session.execute(stmt).scalar_one_or_none()

    if benchmark is not None:
        return benchmark

    # Create new benchmark if not found
    benchmark = Benchmark(name=name)
    db.session.add(benchmark)
    try:
        db.session.commit()
    except IntegrityError:
        # Most likely race condition, retry fetching
        db.session.rollback()
        benchmark = db.session.execute(stmt).scalar_one_or_none()
    return benchmark


def get_result(name: str) -> Result:
    """Retrieve a result by name, or create it if it does not exist."""
    stmt = select(Result).where(Result.name == name)
    result = db.session.execute(stmt).scalar_one_or_none()

    if result is not None:
        return result

    # Create new result if not found
    result = Result(name=name)
    db.session.add(result)
    try:
        db.session.commit()
    except IntegrityError:
        # Most likely race condition, retry fetching
        db.session.rollback()
        result = db.session.execute(stmt).scalar_one_or_none()
    return result


def get_hostname(name: str) -> Hostname:
    """Retrieve a hostname by name, or create it if it does not exist."""
    stmt = select(Hostname).where(Hostname.name == name)
    hostname = db.session.execute(stmt).scalar_one_or_none()

    if hostname is not None:
        return hostname

    # Create new hostname if not found
    hostname = Hostname(name=name)
    db.session.add(hostname)
    try:
        db.session.commit()
    except IntegrityError:
        # Most likely race condition, retry fetching
        db.session.rollback()
        hostname = db.session.execute(stmt).scalar_one_or_none()
    return hostname

# Department and User Management Methods


def get_department(department_id: int) -> Department | None:
    """Retrieve a department by ID."""
    return db.session.get(Department, department_id)


def get_department_by_name(name: str) -> Department | None:
    """Retrieve a department by name."""
    stmt = select(Department).where(Department.name == name)
    return db.session.execute(stmt).scalar_one_or_none()


def create_department(name: str) -> Department:
    """Create a new department."""
    department = Department(name=name)
    db.session.add(department)
    db.session.commit()
    return department


def delete_department(department_id: int) -> bool:
    """Delete a department and all its user assignments."""
    department = get_department(department_id)
    if department:
        stmt = (
            select(BearerToken)
            .where(BearerToken.department_id == department_id)
        )
        tokens = db.session.execute(stmt).scalars().all()
        for token in tokens:
            token.is_active = False

        db.session.delete(department)
        db.session.commit()
        return True
    return False


def get_user_departments(user_handle: str) -> list[Department]:
    """Return all Department rows linked to user_handle (may be empty)."""
    stmt = (
        select(Department)
        .join(DepartmentUser, Department.id == DepartmentUser.department_id)
        .where(DepartmentUser.user_handle == user_handle)
        .order_by(Department.name)
        .distinct()
    )
    return db.session.execute(stmt).scalars().all()


def get_department_users(department_id: int) -> list[DepartmentUser]:
    """Get all users in a department."""
    stmt = select(DepartmentUser).where(
        DepartmentUser.department_id == department_id
    )
    return db.session.execute(stmt).scalars().all()


def add_user_to_department(department_id: int, user_handle: str) \
      -> DepartmentUser:
    """Add a user to a department."""
    dept_user = DepartmentUser(
        department_id=department_id,
        user_handle=user_handle
    )
    db.session.add(dept_user)
    db.session.commit()
    return dept_user


def remove_user_from_department(department_id: int, user_handle: str) -> bool:
    """Remove a user from a department."""
    stmt = select(DepartmentUser).where(
        and_(
            DepartmentUser.department_id == department_id,
            DepartmentUser.user_handle == user_handle
        )
    )
    dept_user = db.session.execute(stmt).scalar_one_or_none()
    if dept_user:
        db.session.delete(dept_user)
        db.session.commit()
        return True
    return False


def get_all_departments_with_access(user_handle: str,
                                    is_super_admin: bool) -> list[Department]:
    """Get all departments that a user has access to."""
    if is_super_admin:
        stmt = select(Department).order_by(Department.name)
        return db.session.execute(stmt).scalars().all()

    # Get user's department
    return get_user_departments(user_handle)


def get_all_users_with_departments() -> list[dict]:
    """Get all users with their department assignments."""
    stmt = select(DepartmentUser).join(Department)

    dept_users = db.session.execute(stmt).scalars().all()

    # Manually construct the response to avoid serialization issues
    return [
        {
            'handle': du.user_handle,
            'department_id': du.department_id,
            'department_name': du.department.name if du.department else None
        }
        for du in dept_users
    ]


def compute_filter(column, options_list):
    """Creates a filter on a column based on equality"""
    # set to make sure there is at most 1 None or null
    options = set(options_list)
    filters = []

    # Discard none and nulls
    if None in options or "null" in options:
        options.discard(None)
        options.discard("null")
        filters.append(column.is_(None))

    # Add all other options (str or id)
    if options:
        filters.append(column.in_(options))

    if len(filters) > 0:
        return or_(*filters)
    return None


def compute_filter_minmax(column, min_value, max_value):
    """Creates a filter on column for min and max values"""
    filters = []
    if min_value:
        filters.append(column >= min_value)
    if max_value:
        filters.append(column <= max_value)

    if len(filters) > 0:
        return and_(*filters)
    return None


def compute_authorized_subquery(user_handle: str,
                                is_super_admin: bool) -> Subquery:

    departments = get_all_departments_with_access(user_handle, is_super_admin)
    departments = list(map(lambda s: s.id, departments))

    filters = compute_filter(Metadata.department_id, departments)

    # Start creating base query

    # The filters might be None because we do not assign files to departments
    stmt = select(Metadata)
    if is_super_admin:
        pass
    elif filters is not None:
        stmt = stmt.where(filters)
    else:
        stmt = stmt.where(sql.false())
    return stmt.subquery()


def execute_query(
    user_handle: str,
    is_super_admin: bool,
    min_time: datetime | None = None,
    max_time: datetime | None = None,
    departments: list[int | str | None] = [],
    benchmarks: list[int | str | None] = [],
    results: list[int | str | None] = [],
    hostnames: list[int | str | None] = [],
    search_string: str | None = None,
    page: int = 0,
    page_size: int = 20,
    ids_only: bool = False
) -> dict | list[str]:
    """
    Executes a query against the Metadata table using a variety of filters,
    returning either a paginated set of metadata records or only their IDs.

    Filters can be applied to restrict results by time range, department,
    benchmark, result type, hostname, and filename search string.

    Returns:
        list[str]: If `ids_only` is True, returns a list of metadata IDs.
        dict: If `ids_only` is False, returns a dictionary with:
            - "filters": Dictionary of filter metadata
                (e.g., available departments with counts).
            - "pagination": Info curent page, page size, and total count.
            - "data": List of metadata records as dictionaries.
    """

    # Compute subquery of whats allowed
    base_subquery = compute_authorized_subquery(user_handle, is_super_admin)
    mdt_alias = aliased(Metadata, base_subquery)

    # Time filters
    time_filter = compute_filter_minmax(
        mdt_alias.time_created, min_time, max_time)

    # Department filters
    dep_filter = compute_filter(mdt_alias.department_id, departments)

    # Benchmarks filters
    bench_filter = compute_filter(mdt_alias.benchmark_id, benchmarks)

    # Result filters
    result_filter = compute_filter(mdt_alias.result_id, results)

    # Hostname filters
    host_filter = compute_filter(mdt_alias.hostname_id, hostnames)

    # Search filters
    search_filter = None
    if search_string:
        search_filter = mdt_alias.filename.ilike(f"%{search_string}%")

    # Compute data for filter selection
    # Can add enums for roles.
    # Can also add special role for time, so we can produce a histogram
    # To make date selection easier
    data_for_filters = get_filters_data(mdt_alias, [
        ("department", Department, dep_filter, Filter_type.STANDARD),
        ("benchmark", Benchmark, bench_filter, Filter_type.STANDARD),
        ("result", Result, result_filter, Filter_type.STANDARD),
        ("hostname", Hostname, host_filter, Filter_type.STANDARD),
        ("time", datetime, time_filter, Filter_type.MINMAXTIME),
        ("search", Department, search_filter, Filter_type.OTHER)
    ])

    # Apply all filters
    filters = []
    for f in [dep_filter, bench_filter, result_filter, host_filter,
              time_filter, search_filter]:
        if f is not None:
            filters.append(f)

    # Build query for data
    data_stmt = select(mdt_alias).select_from(mdt_alias)
    ids_stmt = select(mdt_alias.id).select_from(mdt_alias)
    count_stmt = select(func.count()).select_from(mdt_alias)

    if len(filters) > 0:
        data_stmt = data_stmt.where(and_(*filters))
        ids_stmt = ids_stmt.where(and_(*filters))
        count_stmt = count_stmt.where(and_(*filters))

    # return early if only ids
    if ids_only:
        return db.session.execute(ids_stmt).scalars().all()

    # Count the total number of results for pagination
    total_count = db.session.execute(count_stmt).scalar()

    # Apply pagination and ordering
    data_stmt = data_stmt.order_by(mdt_alias.time_created.desc())
    data_stmt = data_stmt.offset(page * page_size).limit(page_size)

    data = db.session.execute(data_stmt).scalars().all()

    # Structure of the output
    return {
        "filters": data_for_filters,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count
        },
        "data": [item.to_dict() for item in data]
    }


def exclude_filter(current_filter, filters):
    """Helper which returns all filters except the current one"""
    return [f for f in filters if f is not None and f is not current_filter]


def get_filters_data(subq, filters_data):
    """
    Computes dynamic filter options and statistics
    for use in UI filtering components.

    This function processes metadata relationships and returns both the full
    set of available options and their associated counts, based on the
    currently applied filters. It also supports special handling for
    time-based filters.

    Args:
        subq: A SQLAlchemy subquery or aliased Metadata query, typically
            pre-filtered by allowed departments or authorization logic.
        filters_data: A list of filter descriptors, each a tuple of:
            - label: The identifier used as a key
                in the returned dictionary.
            - model: The related table or indicator of filter type.
            - cur_filter: The filter clause to apply for this filter.
            - role (Filter_type enum): The filter role, one of:
                - "STANDARD": Basic categorical filter
                    (e.g., department, result, benchmark).
                - "MINMAXTIME": Time-based range filter
                    (e.g., for histograms or date sliders).
                - "OTHER": does nothing

    Returns:
        dict: A dictionary mapping each `label` to its filter metadata:
            For "STANDART" roles:
                {
                    "label": [
                        {"name": str, "id": int, "count": int},
                        ...
                    ]
                }

                - "name": Name of the model entry (or "None" if missing).
                - "id": Primary key of the model entry.
                - "count": Number of matching metadata entries
                    when all filters are applied.

            For "MinMaxTime" roles:
                {
                    "label": {
                        "local_min_value": datetime | None,
                        "local_max_value": datetime | None,
                        "global_min_value": datetime | None,
                        "global_max_value": datetime | None
                    }
                }

                - "local_*": Date range of current set (all filters applied).
                - "global_*": Date range over entire set (no filters applied).

    Notes:
        - If a filter is not currently active, the counts indicate how many
            results would appear if that filter value were selected.
        - All possible options are included to show the all available choices.
    """

    filters_list = {}

    all_filters = [row[2] for row in filters_data]

    for (label, model, cur_filter, role) in filters_data:

        # Standard filter for
        if role == Filter_type.STANDARD:
            cur_filter_list = exclude_filter(cur_filter, all_filters)
            stmt = select(model.name, model.id, func.count()) \
                .select_from(subq).outerjoin(model).group_by(model.id)

            rows_all = db.session.execute(stmt).all()

            if cur_filter_list:
                stmt = stmt.where(and_(*cur_filter_list))

            rows = db.session.execute(stmt).all()

            filtered_counts = {r[1]: r[2] for r in rows}  # {id: count}

            # Merge with all available options
            merged = []
            for name, id_, _ in rows_all:
                count = filtered_counts.get(id_, 0)
                merged.append({
                    "name": name or "None",
                    "id": id_,
                    "count": count
                })

            filters_list[label] = merged

        elif role == Filter_type.MINMAXTIME:
            # Columns have to be changed manually
            # For other data to work on minMax as well
            cur_filter_list = exclude_filter(cur_filter, all_filters)
            stmt = select(func.min(subq.time_created),
                          func.max(subq.time_created)) \
                .select_from(subq)

            global_min_value, global_max_value = db.session.execute(stmt).one()

            if cur_filter_list:
                stmt = stmt.where(and_(*cur_filter_list))

            local_min_value, local_max_value = db.session.execute(stmt).one()

            filters_list[label] = {
                "local_min_value": local_min_value,
                "local_max_value": local_max_value,
                "global_min_value": global_min_value,
                "global_max_value": global_max_value
            }

    return filters_list


def create_bearer_token(department_id: int,
                        machine_name: str, created_by: str) -> BearerToken:
    """Create a new bearer token for a department."""
    token = BearerToken(
        token=str(uuid.uuid4()),
        machine_name=machine_name,
        department_id=department_id,
        created_by=created_by
    )
    db.session.add(token)
    db.session.commit()
    return token


def get_bearer_tokens_for_departments(department_ids: list[int]) \
        -> list[BearerToken]:
    """Get all bearer tokens for the specified departments."""
    stmt = (
        select(BearerToken)
        .where(
            and_(
                BearerToken.department_id.in_(department_ids),
                BearerToken.is_active
            )
        )
        .order_by(BearerToken.created_at.desc())
    )
    return db.session.execute(stmt).scalars().all()


def get_bearer_token_by_token(token_str: str) -> BearerToken | None:
    """Get a bearer token by its token string."""
    stmt = select(BearerToken).where(
        and_(
            BearerToken.token == token_str,
            BearerToken.is_active
        )
    )
    return db.session.execute(stmt).scalar_one_or_none()


def revoke_bearer_token(token_id: int) -> bool:
    """Revoke a bearer token by setting is_active to False."""
    token = db.session.get(BearerToken, token_id)
    if token:
        token.is_active = False
        db.session.commit()
        return True
    return False


def update_bearer_token_last_used(token: BearerToken) -> None:
    """Update the last_used timestamp for a bearer token."""
    token.last_used = func.now()
    db.session.commit()


def verify_bearer_token_access(token_id: int, user_departments: list[int])\
                                -> bool:
    """Verify if a user has access to manage a specific bearer token."""
    token = db.session.get(BearerToken, token_id)
    if not token:
        return False
    return token.department_id in user_departments
