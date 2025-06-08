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

    it('should navigate to Admin Login when Admin button is clicked', () => {
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

    it('renders the choose screen title', () => {
    cy.get('h2').should('contain.text', 'Choose Screen'); // or from `t.chooseScreen`
  });

    it('displays both Admin and User buttons with correct classes', () => {
    cy.get('[data-testid="home-screen-admin-button"]')
      .should('have.class', 'button')
      .and('have.class', 'btn-blue')
      .and('have.attr', 'href', '/admin');

    cy.get('[data-testid="home-screen-user-button"]')
      .should('have.class', 'button')
      .and('have.class', 'btn-blue')
      .and('have.attr', 'href', '/manual-conversion');
  });

    it('has no extra UI artifacts or broken components', () => {
    cy.get('.small-panel').should('exist');
    cy.get('.card').should('exist');
    cy.get('.button-container').children().should('have.length', 2);
  });
})