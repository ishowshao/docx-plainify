"""
Command-line interface for docx-plainify.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

from .converter import DocxToYamlConverter


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration.
    
    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('-o', '--output', 'output_file', type=click.Path(path_type=Path),
              help='Output YAML file path. If not specified, uses input filename with .yaml extension.')
@click.option('--describe-images', is_flag=True, default=False,
              help='Generate descriptions for images using LLM (requires OpenAI API key)')
@click.option('--api-key', type=str, envvar='OPENAI_API_KEY',
              help='OpenAI API key for image descriptions (can also be set via OPENAI_API_KEY env var)')
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Enable verbose logging')
@click.version_option(version='1.0.0', prog_name='docx-plainify')
def main(input_file: Path, output_file: Optional[Path], describe_images: bool, 
         api_key: Optional[str], verbose: bool) -> None:
    """
    Convert DOCX files to structured YAML format for AI processing.
    
    INPUT_FILE: Path to the input .docx file to convert.
    
    Examples:
    
        # Basic conversion
        docx-plainify document.docx
        
        # Specify output file
        docx-plainify document.docx -o output.yaml
        
        # Include image descriptions (requires OpenAI API key)
        docx-plainify document.docx --describe-images --api-key your_api_key
        
        # Use environment variable for API key
        export OPENAI_API_KEY=your_api_key
        docx-plainify document.docx --describe-images
    """
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Validate input file
        if not input_file.suffix.lower() == '.docx':
            raise click.BadParameter("Input file must be a .docx file")
        
        # Determine output file path
        if output_file is None:
            output_file = input_file.with_suffix('.yaml')
        
        # Validate image description requirements
        if describe_images and not api_key:
            logger.warning("Image descriptions requested but no API key provided. "
                         "Set OPENAI_API_KEY environment variable or use --api-key option.")
            describe_images = False
        
        # Create converter
        converter = DocxToYamlConverter(
            describe_images=describe_images,
            api_key=api_key
        )
        
        # Perform conversion
        logger.info(f"Converting {input_file} to {output_file}")
        converter.convert_file(str(input_file), str(output_file))
        
        click.echo(f"✅ Conversion completed successfully!")
        click.echo(f"📄 Input: {input_file}")
        click.echo(f"📝 Output: {output_file}")
        
        if describe_images and api_key:
            click.echo("🖼️  Image descriptions included")
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 