"""
HelloSynk CLI - Command-line interface for interacting with HelloSynk
"""

import asyncio
import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from hellosynk import HelloSynk
from hellosynk.core.llm import LLMProvider
from hellosynk.skills import SkillRegistry

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """HelloSynk - An open-source, local-first operating system for personal AI agents"""
    pass


@cli.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--provider", type=click.Choice(["openai", "anthropic"]), default="openai")
@click.option("--model", help="LLM model to use")
@click.option("--api-key", help="API key for LLM provider")
def chat(query, provider, model, api_key):
    """Process a query with HelloSynk"""
    query_text = " ".join(query)
    
    async def run():
        hellosynk = HelloSynk(
            llm_provider=LLMProvider(provider),
            llm_model=model,
            llm_api_key=api_key,
        )
        await hellosynk.initialize()
        
        console.print(f"[bold blue]Query:[/bold blue] {query_text}\n")
        
        result = await hellosynk.process(query_text)
        
        console.print(Panel(
            result["response"],
            title="[bold green]Response[/bold green]",
            border_style="green"
        ))
        
        if result.get("executions"):
            console.print("\n[bold]Executed Skills:[/bold]")
            for execution in result["executions"]:
                status_emoji = "✅" if execution["status"] == "success" else "❌"
                console.print(f"{status_emoji} {execution['skill']}: {execution['status']}")
    
    asyncio.run(run())


@cli.group()
def skill():
    """Manage skills"""
    pass


@skill.command("list")
def skill_list():
    """List all installed skills"""
    async def run():
        registry = SkillRegistry()
        await registry.load_skills()
        
        skills = registry.list_skills()
        
        if not skills:
            console.print("[yellow]No skills installed[/yellow]")
            return
        
        table = Table(title="Installed Skills")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="magenta")
        table.add_column("Version", style="green")
        table.add_column("Author", style="yellow")
        table.add_column("Status", style="blue")
        
        for skill_info in skills:
            status = "✅ Enabled" if skill_info["enabled"] else "❌ Disabled"
            table.add_row(
                skill_info["name"],
                skill_info["description"],
                skill_info["version"],
                skill_info["author"],
                status,
            )
        
        console.print(table)
    
    asyncio.run(run())


@skill.command("enable")
@click.argument("skill_name")
def skill_enable(skill_name):
    """Enable a skill"""
    async def run():
        registry = SkillRegistry()
        await registry.load_skills()
        
        try:
            registry.enable_skill(skill_name)
            console.print(f"[green]✓[/green] Enabled skill: {skill_name}")
        except ValueError as e:
            console.print(f"[red]✗[/red] Error: {e}")
    
    asyncio.run(run())


@skill.command("disable")
@click.argument("skill_name")
def skill_disable(skill_name):
    """Disable a skill"""
    async def run():
        registry = SkillRegistry()
        await registry.load_skills()
        
        try:
            registry.disable_skill(skill_name)
            console.print(f"[green]✓[/green] Disabled skill: {skill_name}")
        except ValueError as e:
            console.print(f"[red]✗[/red] Error: {e}")
    
    asyncio.run(run())


@skill.command("install")
@click.argument("skill_path", type=click.Path(exists=True))
def skill_install(skill_path):
    """Install a skill from a file"""
    async def run():
        registry = SkillRegistry()
        await registry.load_skills()
        
        try:
            registry.install_skill(skill_path)
            console.print(f"[green]✓[/green] Installed skill from: {skill_path}")
        except Exception as e:
            console.print(f"[red]✗[/red] Error: {e}")
    
    asyncio.run(run())


@cli.group()
def memory():
    """Manage memory"""
    pass


@memory.command("search")
@click.argument("query")
@click.option("--limit", default=10, help="Maximum number of results")
def memory_search(query, limit):
    """Search memory"""
    async def run():
        hellosynk = HelloSynk()
        await hellosynk.initialize()
        
        results = await hellosynk.search_memory(query, limit=limit)
        
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return
        
        console.print(f"[bold]Found {len(results)} results:[/bold]\n")
        
        for i, node in enumerate(results, 1):
            console.print(Panel(
                node.content,
                title=f"[bold]{i}. {node.type.value}[/bold]",
                border_style="blue"
            ))
            console.print()
    
    asyncio.run(run())


@memory.command("add")
@click.argument("content")
@click.option("--type", type=click.Choice(["entity", "event", "concept", "task", "context"]), default="context")
@click.option("--importance", type=float, default=0.5, help="Importance (0.0 to 1.0)")
def memory_add(content, type, importance):
    """Add a memory"""
    async def run():
        from hellosynk.core.memory import NodeType
        
        hellosynk = HelloSynk()
        await hellosynk.initialize()
        
        node_type = NodeType(type)
        node_id = await hellosynk.add_memory(
            content=content,
            node_type=node_type,
            importance=importance,
        )
        
        console.print(f"[green]✓[/green] Added memory: {node_id}")
    
    asyncio.run(run())


@cli.group()
def config():
    """Manage configuration"""
    pass


@config.command("set-llm")
@click.option("--provider", type=click.Choice(["openai", "anthropic"]), required=True)
@click.option("--model", help="Model name")
@click.option("--api-key", help="API key")
def config_set_llm(provider, model, api_key):
    """Set LLM configuration"""
    async def run():
        hellosynk = HelloSynk()
        await hellosynk.initialize()
        
        try:
            hellosynk.set_llm_config(
                provider=LLMProvider(provider),
                model=model,
                api_key=api_key,
            )
            console.print("[green]✓[/green] LLM configuration updated")
        except Exception as e:
            console.print(f"[red]✗[/red] Error: {e}")
    
    asyncio.run(run())


@config.command("show")
def config_show():
    """Show current configuration"""
    async def run():
        from hellosynk.core.storage import Storage
        
        storage = Storage()
        config = storage.load_config()
        
        console.print(Panel(
            json.dumps(config, indent=2),
            title="[bold]Configuration[/bold]",
            border_style="blue"
        ))
    
    asyncio.run(run())


if __name__ == "__main__":
    cli()


