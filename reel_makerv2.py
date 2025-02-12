from groq import Groq
import requests
import random
import os
from uuid import uuid4
import subprocess
import time
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
import os




console = Console()

SPEAKERS = {
    'american': 'EN-US',
    'british': 'EN-BR',
    'indian': 'EN_INDIA',
    'australian': 'EN-AU',
    'default': 'EN-Default'
}
def generate_story():
    client = Groq(
        api_key="***" # key shown in video is revoke, pls use you own key
    )
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Make a random short and engaging family drama story. Tell the story as if you are the main character, like you are involved in the drama yourself. Make it interesting, full of twists, and avoid making it feel like simple gossip. Keep it short but captivating. Under 170 words but complete and add pauses"
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    
    return chat_completion.choices[0].message.content

def text_to_speech(text, speaker='default', speed='0.8'):
    if speaker not in SPEAKERS:
        print(f"Invalid speaker. Available options: {', '.join(SPEAKERS.keys())}")
        return False
        
    url = "http://127.0.0.1:8888/convert/tts"
    payload = {
        "text": text,
        "speed": speed,
        "language": "EN",
        "speaker_id": SPEAKERS[speaker]
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        with open("narration.wav", "wb") as file:
            file.write(response.content)
        return True
    else:
        print(f"Error in TTS: {response.status_code}, {response.text}")
        return False
def generate_social_content(story):
    client = Groq(
        api_key="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"
    )
    
    prompt = f"""Based on this story, create:
    1. An engaging reel title (max 60 characters)
    2. A compelling description with hashtags (max 200 characters)
    
    Story: {story}"""
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    
    return chat_completion.choices[0].message.content
def process_video(input_video_path, speaker='default', speed='0.8', output_path="final_reel.mp4"):
    """
    Process video with AI narration using ffmpeg.
    
    Args:
        input_video_path (str): Path to input video file
        speaker (str): Speaker accent ('american', 'british', 'indian', 'australian', 'default')
        speed (str): Speech speed (default '0.8')
        output_path (str): Path for output video file
    
    Returns:
        tuple: (story, social_content) if successful, (None, None) if failed
    """
    try:
        # Create temp directory if it doesn't exist
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate unique temp filenames
        temp_id = str(uuid4())
        temp_audio = os.path.join(temp_dir, f"narration_{temp_id}.wav")
        temp_video = os.path.join(temp_dir, f"segment_{temp_id}.mp4")
        
        # Update status
        console.print("[yellow]Generating story...[/yellow]")
        
        # Generate story and convert to speech
        story = generate_story()
        
        console.print("[yellow]Converting story to speech...[/yellow]")
        
        # Save audio to temp directory
        if not text_to_speech(story, speaker, speed):
            console.print("[red]Failed to generate speech audio[/red]")
            return None, None
        
        # Generate social media content
        console.print("[yellow]Generating social media content...[/yellow]")
        social_content = generate_social_content(story)
        
        # Get video duration using ffprobe
        console.print("[yellow]Analyzing video duration...[/yellow]")
        video_duration = float(subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_video_path
        ], capture_output=True, text=True).stdout)
        
        # Get audio duration
        console.print("[yellow]Analyzing audio duration...[/yellow]")
        audio_duration = float(subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            'narration.wav'
        ], capture_output=True, text=True).stdout)
        
        # Calculate random start time
        max_start = max(0, video_duration - audio_duration)
        start_time = random.uniform(0, max_start)
        
        # Extract video segment
        console.print("[yellow]Extracting video segment...[/yellow]")
        extract_command = [
            'ffmpeg',
            '-ss', str(start_time),
            '-i', input_video_path,
            '-t', str(audio_duration),
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-async', '1',
            temp_video,
            '-y'
        ]
        subprocess.run(extract_command, capture_output=True)
        
        # Combine video with new audio
        console.print("[yellow]Combining video and audio...[/yellow]")
        combine_command = [
            'ffmpeg',
            '-i', temp_video,
            '-i', 'narration.wav',
            '-filter_complex', '[1:a]adelay=0|0[delayed_audio]',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '[delayed_audio]',
            '-shortest',
            output_path,
            '-y'
        ]
        subprocess.run(combine_command, capture_output=True)
        
        # Clean up temporary files
        console.print("[yellow]Cleaning up temporary files...[/yellow]")
        if os.path.exists(temp_video):
            os.remove(temp_video)
        if os.path.exists("narration.wav"):
            os.remove("narration.wav")
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)
        
        console.print("[green]Processing completed successfully![/green]")
        return story, social_content
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]FFmpeg error: {str(e)}[/red]")
        return None, None
    except Exception as e:
        console.print(f"[red]Error processing video: {str(e)}[/red]")
        return None, None
    finally:
        # Ensure cleanup of temporary files even if an error occurs
        for temp_file in [temp_video, "narration.wav"]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            try:
                os.rmdir(temp_dir)
            except:
                pass

def interactive_menu():
    """Interactive console menu for video processing"""
    console.clear()
    rprint("[bold blue]🎬 AI Video Narrator[/bold blue]")
    rprint("[yellow]Create engaging videos with AI narration[/yellow]\n")

    # Get input video
    while True:
        input_video = Prompt.ask("Enter the path to your video file")
        if os.path.exists(input_video) and input_video.lower().endswith(('.mp4', '.avi', '.mov')):
            break
        rprint("[red]❌ Invalid file path or unsupported format. Please try again.[/red]")

    # Speaker selection
    rprint("\n[bold cyan]Available Speakers:[/bold cyan]")
    for idx, (name, id) in enumerate(SPEAKERS.items(), 1):
        rprint(f"{idx}. [green]{name}[/green] ({id})")
    
    while True:
        choice = Prompt.ask("\nSelect speaker number", default="5")
        try:
            choice = int(choice)
            if 1 <= choice <= len(SPEAKERS):
                speaker = list(SPEAKERS.keys())[choice-1]
                break
        except ValueError:
            pass
        rprint("[red]❌ Invalid choice. Please select a number from the list.[/red]")

    # Speed selection
    speed = Prompt.ask(
        "\nEnter speech speed",
        default="0.8",
        choices=["0.6", "0.7", "0.8", "0.9", "1.0"]
    )

    # Output file
    use_custom_name = Confirm.ask("\nDo you want to specify the output filename?", default=False)
    if use_custom_name:
        output_path = Prompt.ask("Enter output filename (will add .mp4 if needed)")
        if not output_path.lower().endswith('.mp4'):
            output_path += '.mp4'
    else:
        output_path = f"output_{uuid4()}.mp4"

    # Process with progress indication
    with console.status("[bold green]Processing video...") as status:
        rprint("\n[bold]🎯 Starting video processing[/bold]")
        status.update("[bold yellow]Generating story...")
        story, social_content = process_video(
            input_video_path=input_video,
            speaker=speaker,
            speed=speed,
            output_path=output_path
        )

    if story and social_content:
        console.clear()
        rprint("\n[bold green]✅ Processing complete![/bold green]")
        rprint("\n[bold]📖 Generated Story:[/bold]")
        rprint(f"[cyan]{story}[/cyan]")
        rprint("\n[bold]📱 Social Media Content:[/bold]")
        rprint(f"[yellow]{social_content}[/yellow]")
        rprint(f"\n[bold green]💾 Output saved as:[/bold green] {output_path}")
        
    else:
        rprint("\n[bold red]❌ Error processing video. Please try again.[/bold red]")

    # Ask if user wants to process another video
    if Confirm.ask("\nWould you like to process another video?", default=False):
        return True
    return False

if __name__ == "__main__":
    try:
        while True:
            if not interactive_menu():
                rprint("\n[bold blue]👋 Thank you for using AI Video Narrator![/bold blue]")
                break
    except KeyboardInterrupt:
        rprint("\n\n[bold yellow]👋 Program terminated by user[/bold yellow]")
    except Exception as e:
        rprint(f"\n[bold red]❌ An error occurred: {str(e)}[/bold red]")
