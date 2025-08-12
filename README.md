Comp PlaybookThis is a web application designed to serve as an interactive playbook for compliance audits. It helps streamline the audit process by providing a centralized resource for all team members.FeaturesRoles & Responsibilities: A clear breakdown of each team member's role in the compliance process.Audit Lifecycle: A visual guide to the stages of an audit, from preparation to archiving.Interactive Workflow: A linear, visual representation of the end-to-end audit process, including feedback loops.Audit Form: A section for filling out audit-related questions and gathering data.Score Calculator: A tool to help evaluate compliance scores.Supporting Files: A place to link and store important documents.User Accounts: Secure login with two account types:Analysts: Can sign off on playbook completion.Leads: Can view all analyst sign-offs.Getting StartedTo run this application locally, you will need to have Python and Flask installed.PrerequisitesPython 3.10 or higherpip (Python package manager)InstallationClone the repository:git clone https://github.com/your-username/Comp_Playbook.git
cd Comp_Playbook
Create and activate a virtual environment:python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
Install the required packages:pip install Flask Flask-SQLAlchemy Werkzeug
Run the application:python app.py
The application will be accessible at http://127.0.0.1:5000 in your web browser.Technologies UsedFlask: The web framework used to build the application.Flask-SQLAlchemy: An extension for handling database operations.SQLite: The default database used for development.HTML/CSS: For the front-end user interface.
