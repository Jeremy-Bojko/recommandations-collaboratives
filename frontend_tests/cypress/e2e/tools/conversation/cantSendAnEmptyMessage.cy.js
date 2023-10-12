import projects from '../../../fixtures/projects/projects.json'

const currentProject = projects[1];

describe("I can't send an empty message", () => {
    beforeEach(() => {
        cy.login("jean");
    })

    it('shows a disabled send message button', () => {
        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({ force: true });

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        cy.get('[data-test-id="send-message-conversation"]').should('have.attr', 'disabled')
    })

    it('enables the send message if I type a message', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({ force: true });

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        cy.get('[data-test-id="tiptap-editor-content"] .ProseMirror').type(`new message`, { force: true })

        cy.get('[data-test-id="send-message-conversation"]').should('not.have.attr', 'disabled')
    })

    it('disables the send message if I erase my message (empty message)', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({ force: true });

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        cy.get('[data-test-id="tiptap-editor-content"] .ProseMirror').type(`new message`, { force: true })

        cy.get('[data-test-id="send-message-conversation"]').should('not.have.attr', 'disabled')

        cy.get('[data-test-id="tiptap-editor-content"] .ProseMirror').clear()

        cy.get('[data-test-id="send-message-conversation"]').should('have.attr', 'disabled')
    })

})
