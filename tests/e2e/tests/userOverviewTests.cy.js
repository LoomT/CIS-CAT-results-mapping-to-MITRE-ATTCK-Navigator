describe('UserScreen UI Tests (Frontend Only)', () => {
  beforeEach(() => {
    cy.visit('/manual-upload');
  });

  it('renders the user screen title and layout sections', () => {
    cy.get('[data-testid="user-screen-page-title"]')
      .should('be.visible')
      .and('contain.text', 'Manual Upload');

    cy.get('[data-testid="user-screen-upload-section"]').should('be.visible');
    cy.get('[data-testid="user-screen-file-table-section"]').should('be.visible');
  });

  it('shows upload instructions and file input trigger', () => {
    cy.get('[data-testid="user-screen-upload-section"]').within(() => {
      cy.contains('Drag and drop');
      cy.contains('Choose file').should('exist');
    });
  });

  // it('opens the file dialog when "Choose File" button is clicked', () => {
  //   cy.get('[data-testid="user-screen-upload-section"] button')
  //     .contains('Choose file')
  //     .click();

  //   cy.get('#file-input').should('exist');
  // });

  it('renders table headers correctly', () => {
    cy.get('[data-testid="user-screen-file-table-section"]').within(() => {
      cy.get('thead tr').within(() => {
        cy.contains('th', 'Name');
        cy.contains('th', 'Department');
        cy.contains('th', 'Date');
        cy.contains('th', 'Actions');
      });
    });
  });

  it('shows no files in table by default', () => {
    cy.get('[data-testid="user-screen-file-table-section"] tbody tr').should('have.length', 0);
  });

  it('handles drag enter and leave visually', () => {
    cy.get('.upload-area')
      cy.get('.upload-area').trigger('dragenter');
      cy.get('.upload-area').should('have.class', 'drag-active');

      cy.get('.upload-area').trigger('dragleave');
      cy.get('.upload-area').should('not.have.class', 'drag-active');
  });
});
