describe('HomeScreen tests', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should navigate to User Overview when User button is clicked', () => {
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

  it('should navigate to Admin overview when Admin button is clicked', () => {
    // Visit the home page
    cy.visit('/');

    // Find and click the Admin button using its id
    cy.get('[data-testid="home-screen-admin-button"]').should('be.visible')
    cy.get('[data-testid="home-screen-admin-button"]').click();

    // Verify that we navigated to the Admin overview screen
    cy.get('.department-filter-testid').should('exist');
  });

  it('should navigate to User Management when User Management button is clicked', () => {
    // Visit the home page
    cy.visit('/');

    // Find and click the Admin button using its id
    cy.get('[data-testid="home-screen-admin-user-management"]').should('be.visible')
    cy.get('[data-testid="home-screen-admin-user-management"]').click();

    // Verify that we navigated to the Admin overview screen
    cy.get('[data-testid="user-management-dashboard"]').should('exist');
  });
})