describe('Basic application tests', () => {
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

  it("can't access admin overview directly", () => {
    cy.request({
      url: '/admin/overview',
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.eq(404);
    });
  });

  //
  // it('can upload a file', () => {
  //   cy.visit('/')
  //   // Test file upload functionality
  //   cy.get('input[type=file]').selectFile('cypress/fixtures/example.json', { force: true })
  //   cy.get('button[type=submit]').click()
  //   // Add assertions for successful upload
  // })
})