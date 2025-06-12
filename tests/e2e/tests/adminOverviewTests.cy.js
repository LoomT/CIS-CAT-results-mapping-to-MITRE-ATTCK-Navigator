describe('AdminOverview UI Tests (Frontend Only)', () => {
  beforeEach(() => {
    cy.visit('/admin');
    cy.url().should('include', '/admin');
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
    cy.get('table thead').within(() => {
      cy.contains('th', 'Name');
      cy.contains('th', 'Department');
      cy.contains('th', 'Date');
      cy.contains('th', 'Actions');
    });
  });

  it('checkboxes toggle correctly', () => {
    cy.get('input[type="checkbox"]').each(($checkbox) => {
      cy.wrap($checkbox).check();
      cy.wrap($checkbox).should('be.checked');

      cy.wrap($checkbox).uncheck();
      cy.wrap($checkbox).should('not.be.checked');
    });
  });

  it('date inputs accept input', () => {
    const fromDate = '2025-01-01T00:00';
    const toDate = '2025-12-31T23:59';

    cy.get('input[type="datetime-local"]').first().type(fromDate);
    cy.get('input[type="datetime-local"]').first().should('have.value', fromDate);

    cy.get('input[type="datetime-local"]').last().type(toDate);
    cy.get('input[type="datetime-local"]').last().should('have.value', toDate);
  });

  it('search field accepts input', () => {
    cy.get('input[placeholder="Search files..."]').type('type-test');
    cy.get('input[placeholder="Search files..."]').should('have.value', 'type-test');
  });

  it('action column placeholder exists', () => {
    cy.get('table thead').contains('th', 'Actions');
    cy.get('table tbody').then($body => {
      if ($body.find('td').length > 0) {
        cy.get('table tbody td').last().should('exist');
      }
    });
  });

  it('UI does not crash without data', () => {
    cy.get('body').should('not.contain.text', 'Error');
  });
});
