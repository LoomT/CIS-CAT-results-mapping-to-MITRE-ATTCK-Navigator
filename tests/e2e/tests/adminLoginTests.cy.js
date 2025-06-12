describe('AdminLogin Component Tests', () => {
  beforeEach(() => {
    cy.visit('/admin');
  });

  it('renders the login page correctly', () => {
    cy.get('[data-testid="login-screen"]').should('exist');
    cy.get('[data-testid="admin-login-page-title"]').should('contain.text', 'Admin Login');
    cy.get('[data-testid="password-field"]').should('exist');
  });

  it('allows typing into the token field', () => {
    cy.get('[data-testid="password-field"]').type('test-token');
    cy.get('[data-testid="password-field"]').should('have.value', 'test-token');
  });

  it('shows error message for incorrect token', () => {
    cy.get('[data-testid="password-field"]').type('wrong-token');
    cy.contains('button', 'Enter').click();
    cy.contains('Token Incorrect').should('exist');
  });

  it('navigates to admin overview with correct token', () => {
    cy.get('[data-testid="password-field"]').type('correct-token');
    cy.contains('button', 'Enter').click();
    cy.url().should('include', '/admin/overview');
  });

  it('submits form when Enter key is pressed', () => {
    cy.get('[data-testid="password-field"]').type('correct-token{enter}');
    cy.url().should('include', '/admin/overview');
  });

  it('toggles password visibility', () => {
    cy.get('[data-testid="password-field"]').type('testtoken');
    cy.get('.toggle-visibility-icon').click();
    cy.get('[data-testid="password-field"]').should('have.attr', 'type', 'text');
    cy.get('.toggle-visibility-icon').click();
    cy.get('[data-testid="password-field"]').should('have.attr', 'type', 'password');
  });
});
