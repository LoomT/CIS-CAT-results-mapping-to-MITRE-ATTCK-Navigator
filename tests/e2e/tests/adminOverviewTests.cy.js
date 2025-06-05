describe('AdminOverview tests', () => {
  it('displays all filter controls', () => {
    cy.visit('/admin');
    cy.get('[data-testid="password-field"]').type('correct-token{enter}', { force: true });

    cy.get('[data-testid="department-filter"]').should('exist');
    cy.get('input[type="text"][placeholder="Search hosts..."]').should('exist');
    cy.get('input[type="checkbox"]').should('exist');
    cy.get('input[type="datetime-local"]').should('have.length', 2); // from and to
    cy.get('[data-testid="benchmark-filter"]').should('exist');
  });

  it('renders file table headers correctly', () => {
    cy.visit('/admin');
    cy.get('[data-testid="password-field"]').type('correct-token{enter}', { force: true });

    cy.get('table.files-table thead').within(() => {
      cy.contains('th', 'Name');
      cy.contains('th', 'Department');
      cy.contains('th', 'Date');
      cy.contains('th', 'Actions');
    });

    cy.get('table.files-table tbody tr').should('have.length', 0); // because files = []
  });
});

describe('AdminOverview security', () => {
  it("can't access admin overview directly", () => {
    cy.request({
      url: '/admin/overview',
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.eq(404);
    });
  });
})