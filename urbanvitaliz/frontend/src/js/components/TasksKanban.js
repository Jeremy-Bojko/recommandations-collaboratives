import Alpine from "alpinejs"
import TaskApp from './Tasks'
import { TASK_STATUSES } from '../config/statuses';

Alpine.data("KanbanTasks", boardTasksApp)

export default function boardTasksApp(projectId) {

    const app = {
        boards: [
            { status: TASK_STATUSES.PROPOSED, title: "Nouvelles ", color_class: "border-primary", color: "#0d6efd" },
            { status: TASK_STATUSES.INPROGRESS, title: "En cours", color_class: "border-secondary", color: "#6c757d" },
            { status: TASK_STATUSES.BLOCKED, title: "En attente", color_class: "border-warning", color: "#ffc107" },
            { status: [TASK_STATUSES.DONE, TASK_STATUSES.NOT_INTERESTED, TASK_STATUSES.ALREADY_DONE], title: "Archivées", color_class: "border-error", color: "#adb5bd" },
        ],
        onDragStart(event, uuid) {
            event.dataTransfer.clearData();
            event.dataTransfer.effectAllowed = "move";
            event.dataTransfer.setData('application/uuid', uuid);
            event.target.classList.add('drag-dragging');
            document.querySelectorAll(".drop-column").forEach(e => e.classList.add("drop-highlight"));
        },
        onDragEnd(event) {
            event.target.classList.remove('drag-dragging');
            document.querySelectorAll(".drop-column").forEach(e => e.classList.remove("drop-highlight"));
        },
        onDragEnter(event) {
            if (this.currentlyHoveredElement && this.currentlyHoveredElement !== event.currentTarget) {
                this.currentlyHoveredElement.classList.remove('drag-target');
            }
            this.currentlyHoveredElement = event.currentTarget;
            event.currentTarget.classList.add('drag-target');
        },
        onDragLeave(event) {
            if (event.target === this.currentlyHoveredElement) {
                event.target.classList.remove('drag-target');
            }
        },
        onDragOver(event) {
            event.preventDefault();
            event.dataTransfer.dropEffect = "move";
        },
        async onDrop(event, status, targetUuid) {
            event.preventDefault();

            console.log('board status ? ', status);

            this.currentlyHoveredElement.classList.remove('drag-target');
            this.currentlyHoveredElement = null;

            const uuid = event.dataTransfer.getData("application/uuid");

            const data = this.findByUuid(uuid)
            const nextData = this.findByUuid(targetUuid)

            if (status instanceof Array) {
                if (this.isArchivedStatus(data.status) && nextData) {
                    await this.$store.tasksData.moveTask(data.id, nextData.id);
                } else {
                    this.handleOpenFeedbackModal(data);
                }
            } else {
                await this.$store.task.issueFollowup(data, status);
                if (nextData) await this.$store.tasksData.moveTask(data.id, nextData.id);
            }

            await this.$store.tasksData.getTasks()
        }    
    }

    return TaskApp(app, projectId)
}
