import click

from .command import Service

@click.command()
@click.help_option("-h", "--help")
@click.option("--scene", required=True, type=str, help="Arquivo JSON da cena")
@click.option("--output", required=True, type=str, help="Arquivo Markdown de saída")
def main(scene: str, output: str) -> None: 
    service = Service()
    service.run(file_scene=scene, file_md=output)

if __name__ == "__main__":
    main()
