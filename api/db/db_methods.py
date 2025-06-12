# A file for database methods for querrying and manipulating the database.
from datetime import datetime
from sqlalchemy import Subquery, select, func, and_, or_, sql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from enum import Enum

try:
    from db.models import Metadata, Benchmark, Department, Result, Hostname, \
        DepartmentUser
    from db.db import db
except ImportError:
    from .models import Metadata, Benchmark, Department, Result, Hostname, \
        DepartmentUser
    from .db import db


class Filter_type(Enum):
    STANDARD = 1
    MINMAXTIME = 2
    OTHER = 3


def get_metadata(args, ids: bool = False) -> dict | list[str]:
    """Converting from arguments in request.args to function arguments."""
    return execute_query(
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
        db.session.delete(department)
        db.session.commit()
        return True
    return False


def get_user_department(user_handle: str) -> int | None:
    """Get the department ID that a user is assigned to (if any)."""
    stmt = select(DepartmentUser.department_id).where(
        DepartmentUser.user_handle == user_handle
    )
    result = db.session.execute(stmt).scalar_one_or_none()
    return result


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
    user_dept_id = get_user_department(user_handle)
    if user_dept_id:
        return [get_department(user_dept_id)]
    return []


def get_all_users_with_departments(is_super_admin: bool,
                                   user_handle: str) -> list[dict]:
    """Get all users with their department assignments."""
    if is_super_admin:
        stmt = select(DepartmentUser).join(Department)
    else:
        # Department admins only see users in their department
        user_dept_id = get_user_department(user_handle)
        if not user_dept_id:
            return []
        stmt = select(DepartmentUser).where(
            DepartmentUser.department_id == user_dept_id
        ).join(Department)
    
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


# TODO: Add department filter which comes from request token
# Might need to swap to names to be able to create them on the spot
def get_allowed_departments() -> list[int | None]:
    return [None, 1, 2]  # Placeholder for actual department retrieval


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
    if filters:
        return or_(*filters)
    return None


def compute_filter_minmax(column, min_value, max_value):
    """Creates a filter on column for min and max values"""
    filters = []
    if min_value:
        filters.append(column >= min_value)
    if max_value:
        filters.append(column <= max_value)

    if filters:
        return and_(*filters)
    return None


def compute_authorized_subquery() -> Subquery:

    departments = get_allowed_departments()
    filters = compute_filter(Metadata.department_id, departments)

    # If no departments are available, make query return nothing
    if departments == []:
        filters.append(sql.false())

    # Start creating base query
    stmt = select(Metadata)
    if filters is not None:
        stmt = stmt.where(filters)
    return stmt.subquery()


def execute_query(
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
    base_subquery = compute_authorized_subquery()
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

    if filters is not None:
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

        # Standart filter for
        if role == Filter_type.STANDARD:
            cur_filter_list = exclude_filter(cur_filter, all_filters)
            stmt = select(model.name, model.id, func.count()) \
                .select_from(subq).join(model, full=True).group_by(model.id)
            # TODO: Fix it using full outer join to only need 1 SQL
            # For now, it is merged in python for simplicity

            # UPDATE: So full outer join does exist, it just does not work?
            # Will solve it tmr to return zeroes as well.
            # I think I need to do one more subquery,
            # So where clause is before full outer join

            # Temp? Solution:
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
