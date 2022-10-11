//Must be dore after `addARecommandationAsASwitchtender.cy.js`
describe('I can comment & interact with a recommandation', () => {
    beforeEach(() => {
        cy.login("switchtender");
    })

    it('goes to recommandation page', () => {

        cy.visit('/projects')

        cy.contains('[Test] Frites & Friches 🍟').click({force:true});

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains('fake recommandation with no resource').parent().click({force:true});

        const now = new Date();

        cy.get('textarea')
            .type(`test : ${now}`, { force: true })
            .should('have.value', `test : ${now}`)

        cy.contains("Envoyer").click({ force: true })

        cy.contains("test : Thu Oct 06 2022 10:56:50 GMT+0200 (heure d’été d’Europe centrale)")

        cy.get('a').contains("En cours").click({ force: true });

        cy.get('[aria-label="Close"]').click({force:true})
    })
})
