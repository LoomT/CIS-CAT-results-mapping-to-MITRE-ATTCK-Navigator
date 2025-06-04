import AdminOverview from '../../../client/src/AdminOverview.jsx';
import { LanguageContext } from '../../../client/src/main.jsx';

describe('AdminOverview tests', () => {
  it('renders correctly', () => {
    cy.mount(
      <LanguageContext.Provider value={{}}>
        <AdminOverview />
      </LanguageContext.Provider>
    );

    cy.contains('Admin Overview'); // or other assertions
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