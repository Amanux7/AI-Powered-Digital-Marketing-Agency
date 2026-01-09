from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from engine.db.database import get_session, init_db
from engine.models.models import Project, ProjectBase, Run, AgentOutput
from engine.core.config import settings
from engine.core.orchestrator import Orchestrator
from engine.core.compiler import OutputCompiler
from uuid import UUID

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {
        "message": "AI Marketing Agent Engine is operational",
        "status": "healthy",
        "version": "0.1.0-mvp"
    }

@app.post("/projects", response_model=Project)
def create_project(project: ProjectBase, db: Session = Depends(get_session)):
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects", response_model=list[Project])
def list_projects(db: Session = Depends(get_session)):
    return db.query(Project).all()

@app.post("/projects/{project_id}/runs")
async def start_run(project_id: UUID, background_tasks: BackgroundTasks, db: Session = Depends(get_session)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    run = Run(project_id=project_id)
    db.add(run)
    db.commit()
    db.refresh(run)
    
    orchestrator = Orchestrator()
    background_tasks.add_task(orchestrator.execute_run, run.id)
    
    return {"run_id": run.id, "status": "started"}

@app.get("/runs/{run_id}", response_model=Run)
def get_run(run_id: UUID, db: Session = Depends(get_session)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@app.get("/runs/{run_id}/outputs", response_model=list[AgentOutput])
def get_run_outputs(run_id: UUID, db: Session = Depends(get_session)):
    return db.query(AgentOutput).filter(AgentOutput.run_id == run_id).all()

@app.get("/runs/{run_id}/compile")
def compile_run(run_id: UUID, db: Session = Depends(get_session)):
    outputs = db.query(AgentOutput).filter(AgentOutput.run_id == run_id).all()
    if not outputs:
        raise HTTPException(status_code=404, detail="No outputs found for this run")
    
    strategy_markdown = OutputCompiler.compile_strategy(outputs)
    return {"markdown": strategy_markdown}

@app.post("/runs/{run_id}/approve")
def approve_run(run_id: UUID, db: Session = Depends(get_session)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run.status = "approved"
    db.add(run)
    db.commit()
    return {"status": "approved"}
