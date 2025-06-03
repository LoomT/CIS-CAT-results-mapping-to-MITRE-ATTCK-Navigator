describe('HomeScreen tests', () => {
  it('should navigate to User Overview when User button is clicked', () => {
    // Visit the home page
    cy.visit('/');

    // Find and click the User button using its id
    cy.get('[data-testid="home-screen-user-button"]').should('be.visible')
    cy.get('[data-testid="home-screen-user-button"]').click();

    // Verify that we navigated to the User Overview screen
    cy.get('[data-testid="user-screen-page-title"]')
      .should('be.visible')
      .should('have.text', 'User Overview');

    // Additional verification that we're on the User screen
    cy.get('[data-testid="user-screen"]').should('exist');
    cy.get('[data-testid="user-screen-upload-section"]').should('be.visible');
    cy.get('[data-testid="user-screen-file-table-section"]').should('be.visible');
  });

    it('should navigate to Admin Overview when Admin button is clicked', () => {
    // Visit the home page
    cy.visit('/');

    // Find and click the Admin button using its id
    cy.get('[data-testid="home-screen-admin-button"]').should('be.visible')
    cy.get('[data-testid="home-screen-admin-button"]').click();

    // Verify that we navigated to the Admin Login screen
    cy.get('[data-testid="admin-login-page-title"]')
      .should('be.visible')
      .should('have.text', 'Admin Login');

    // Additional verification that we're on the Login screen
    cy.get('[data-testid="login-screen"]').should('exist');
    cy.get('[data-testid="password-field-container"]').should('be.visible');
    cy.get('[data-testid="password-field"]').should('be.visible');
  });

  it("can't access admin overview directly", () => {
    cy.request({
      url: '/admin/overview',
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.eq(404);
    });
  });
})