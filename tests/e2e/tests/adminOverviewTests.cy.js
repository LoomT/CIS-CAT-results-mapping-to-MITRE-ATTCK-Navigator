describe('AdminOverview UI Tests (Frontend Only)', () => {
  beforeEach(() => {
    cy.visit('/admin');
    cy.get('[data-testid="password-field"]').type('correct-token{enter}', { force: true });
    cy.url().should('include', '/admin/overview');
  });

  it('renders filter controls correctly', () => {
    cy.get('.department-filter-testid').should('exist');
    cy.get('.benchmark-filter-testid').should('exist');
    cy.get('.hostname-filter-testid').should('exist');

    cy.get('input[type="checkbox"]').should('exist');
    cy.get('input[placeholder="Search files..."]').should('exist');
    cy.get('input[type="datetime-local"]').should('have.length', 2); // From and To
  });

  it('renders table headers correctly', () => {
    cy.get('table.files-table thead').within(() => {
      cy.contains('th', 'Name');
      cy.contains('th', 'Department');
      cy.contains('th', 'Date');
      cy.contains('th', 'Actions');
    });
  });

  it('renders empty table body by default', () => {
    cy.get('table.files-table tbody tr').should('have.length', 0); // No backend yet
  });

  it('checkboxes toggle correctly', () => {
    cy.get('input[type="checkbox"]').each(($checkbox) => {
      cy.wrap($checkbox).check().should('be.checked');
      cy.wrap($checkbox).uncheck().should('not.be.checked');
    });
  });

  it('date inputs accept input', () => {
    const fromDate = '2025-01-01T00:00';
    const toDate = '2025-12-31T23:59';

    cy.get('input[type="datetime-local"]').first().type(fromDate).should('have.value', fromDate);
    cy.get('input[type="datetime-local"]').last().type(toDate).should('have.value', toDate);
  });

  it('search field accepts input', () => {
    cy.get('input[placeholder="Search files..."]').type('type-test');
    cy.get('input[placeholder="Search files..."]').should('have.value', 'type-test');
  });

  it('dropdowns allow selection (static test)', () => {
    cy.get('.department-filter-testid select').select(0); // Select first option
    cy.get('.benchmark-filter-testid select').select(0);
    cy.get('.hostname-filter-testid select').select(0);
  });

  it('action column placeholder exists', () => {
    cy.get('table.files-table thead').contains('th', 'Actions');
    cy.get('table.files-table tbody').then($body => {
      if ($body.find('td').length > 0) {
        cy.get('table.files-table tbody td').last().should('exist');
      }
    });
  });

  it('UI does not crash without data', () => {
    cy.get('body').should('not.contain.text', 'Error');
  });

  it("can't access overview directly without login", () => {
    cy.visit('/'); // simulate logout or reset
    cy.visit('/admin/overview');
    cy.url().should('not.include', '/admin/overview');
  });
});
