from datetime import datetime, timedelta

from document_management_system import DocumentManagementSystem
from models.user import User
from models.department import Department
from enums import AccessLevelEnum, DocumentTypeEnum, DocumentStatusEnum, PositionEnum, WorkflowStatusEnum, \
    ReportTypeEnum


def run_demo():
    """
    Demonstration of the document management system
    """
    print("Initializing document management system...")
    dms = DocumentManagementSystem()

    print("\n1. Creating users and departments")
    legal_department = Department(name="Legal Department", head=None)

    # Creating the head lawyer
    head_lawyer = User(
        username="lawyer_head",
        password="secure_pwd123",
        position=PositionEnum.HEAD,
        department=None,
        access_level=AccessLevelEnum.ADMIN
    )
    legal_department.head = head_lawyer
    head_lawyer.department = legal_department

    # Adding the head to the system
    dms.add_user(head_lawyer)

    # Creating a regular lawyer
    lawyer = User(
        username="lawyer1",
        password="pwd456",
        position=PositionEnum.EMPLOYEE,
        department=legal_department,
        access_level=AccessLevelEnum.READ_WRITE
    )
    legal_department.add_member(lawyer)

    # Adding the lawyer to the system
    dms.add_user(lawyer)

    # Creating a manager
    manager = User(
        username="manager1",
        password="mgr789",
        position=PositionEnum.MANAGER,
        department=None,
        access_level=AccessLevelEnum.READ_WRITE
    )

    # Adding the manager to the system
    dms.add_user(manager)

    print(f"Created department: {legal_department.name}")
    print(f"Users in the system: {[user.username for user in dms._users]}")

    print("\n2. Creating documents")
    contract = dms.create_document(
        title="Office Lease Agreement",
        content="This agreement is made between LLC 'Company' and Private Entrepreneur 'Landlord' regarding the lease of office space.",
        author=head_lawyer,
        document_type=DocumentTypeEnum.CONTRACT
    )

    policy = dms.create_document(
        title="Corporate Policy",
        content="Rules and standards of conduct for company employees.",
        author=manager,
        document_type=DocumentTypeEnum.POLICY
    )

    print(f"Created documents: {[doc.title for doc in dms._documents]}")

    print("\n3. Setting up document access")
    dms._access_control.grant_access(
        document=contract,
        user=lawyer,
        level=AccessLevelEnum.READ_ONLY
    )

    dms._access_control.grant_access(
        document=policy,
        user=head_lawyer,
        level=AccessLevelEnum.READ_WRITE
    )

    print(
        f"Access to document '{contract.title}' for users: {list(dms._access_control.document_access[contract.id].keys())}")

    print("\n4. Creating a workflow")
    workflow_steps = [
        {"step": "Legal review", "status": DocumentStatusEnum.REVIEW},
        {"step": "Executive signing", "status": DocumentStatusEnum.APPROVAL},
        {"step": "Archiving", "status": DocumentStatusEnum.ARCHIVED}
    ]

    contract_workflow = dms.create_workflow(
        document_type=DocumentTypeEnum.CONTRACT,
        workflow_steps=workflow_steps
    )

    print(f"Created workflow for document type: {contract_workflow.document_type.value}")
    print(f"Workflow steps: {', '.join([step['step'] for step in contract_workflow.workflow_steps])}")

    # Give the head lawyer write access to the document
    dms._access_control.grant_access(
        document=contract,
        user=head_lawyer,
        level=AccessLevelEnum.READ_WRITE
    )

    # Assign workflow to the document
    dms.assign_workflow_to_document(contract, contract_workflow, head_lawyer)

    print("\n5. Working with document versions")
    # Create a branch for working with the contract
    dms.create_branch(contract, "amendments", lawyer)

    # Change the document content and save changes
    original_content = contract.content
    contract.content = original_content + "\nAdditional terms: utility payments are to be made by the tenant."
    dms.commit_changes(contract, lawyer, "Added clause about utility payments")

    # Get version history
    version_history = dms.get_document_version_history(contract)
    print(f"Version history for document '{contract.title}':")
    for version in version_history:
        print(f"  Version {version['version']}, author: {version['author'].username}")

    print("\n6. Searching for documents")
    # Set search criteria
    dms._search_engine.set_criteria({"title": "agreement"})
    search_results = dms.search_documents()
    print(f"Documents found for query 'agreement': {len(search_results)}")
    for doc in search_results:
        print(f"  - {doc.title}")

    print("\n7. Document analysis and related document search")
    keywords = dms.analyze_document(contract)
    print(f"Keywords for document '{contract.title}': {', '.join(list(keywords)[:5])}")

    print("\n8. Assigning a task")
    deadline = datetime.now() + timedelta(days=5)
    task = dms.assign_task(
        document=contract,
        assignee=lawyer,
        deadline=deadline
    )
    print(f"Task assigned to user {task.assignee.username}")
    print(f"Deadline: {task.deadline.strftime('%d.%m.%Y')}")

    print("\n9. Generating a report")
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    report = dms.generate_report(
        report_type=ReportTypeEnum.DOCUMENT_STATUS,
        start_date=start_date,
        end_date=end_date
    )
    print(f"Generated report for period: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")

    print("\n10. Exporting a document to an external system")
    export_result = dms.export_document_to_external_system(contract, "system1", head_lawyer)
    print(f"Export result: {export_result['message']}")

    print("\nDemonstration completed!")


if __name__ == "__main__":
    run_demo()
