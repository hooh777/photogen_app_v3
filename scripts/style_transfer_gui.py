#!/usr/bin/env python3
"""
Style Transfer GUI - Simple interface for the selfie + style reference workflow

Provides an easy-to-use graphical interface for:
1. Selecting selfie image (plain background)
2. Selecting style reference image (scene background)  
3. Generating stylized result

Usage:
    python scripts/style_transfer_gui.py
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
from datetime import datetime
import json

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.style_transfer import StyleTransferProcessor
from core.secure_storage import SecureStorage


class StyleTransferGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoGen Style Transfer")
        self.root.geometry("800x700")
        
        # Initialize processor
        self.processor = None
        self.selfie_path = None
        self.style_path = None
        
        self.setup_ui()
        self.check_api_key()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Style Transfer Workflow", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, 
                                  text="Selfie (Plain Background) + Style Reference (Scene) → Stylized Result",
                                  font=("Arial", 10))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Selfie selection
        selfie_frame = ttk.LabelFrame(main_frame, text="1. Select Selfie (Plain Background)", padding="10")
        selfie_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        selfie_frame.columnconfigure(1, weight=1)
        
        ttk.Button(selfie_frame, text="Browse...", command=self.select_selfie).grid(row=0, column=0, padx=(0, 10))
        self.selfie_label = ttk.Label(selfie_frame, text="No selfie selected", foreground="gray")
        self.selfie_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Style reference selection
        style_frame = ttk.LabelFrame(main_frame, text="2. Select Style Reference (Scene Background)", padding="10")
        style_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        style_frame.columnconfigure(1, weight=1)
        
        ttk.Button(style_frame, text="Browse...", command=self.select_style).grid(row=0, column=0, padx=(0, 10))
        self.style_label = ttk.Label(style_frame, text="No style reference selected", foreground="gray")
        self.style_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="3. Options", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.analyze_only_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Analyze only (don't generate image)", 
                       variable=self.analyze_only_var).grid(row=0, column=0, sticky=tk.W)
        
        # Output directory
        output_frame = ttk.Frame(options_frame)
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, padx=(0, 10))
        self.output_var = tk.StringVar(value="outputs")
        ttk.Entry(output_frame, textvariable=self.output_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="Browse...", command=self.select_output_dir).grid(row=0, column=2)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(20, 10))
        
        self.process_button = ttk.Button(button_frame, text="🎨 Start Style Transfer", 
                                       command=self.start_process, state=tk.DISABLED)
        self.process_button.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔑 Setup API Key", command=self.setup_api_key).grid(row=0, column=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=(5, 10))
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=10, wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def check_api_key(self):
        """Check if API key is configured"""
        try:
            secure_storage = SecureStorage()
            api_key = secure_storage.load_api_key("Qwen-VL-Max (Alibaba Cloud)")
            if api_key:
                self.status_label.config(text="API key configured ✓", foreground="green")
                self.update_process_button_state()
            else:
                self.status_label.config(text="API key not configured", foreground="orange")
        except Exception as e:
            self.status_label.config(text=f"Error checking API key: {e}", foreground="red")
    
    def select_selfie(self):
        """Select selfie image file"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Selfie Image (Plain Background)",
            filetypes=filetypes
        )
        
        if filename:
            self.selfie_path = filename
            self.selfie_label.config(text=Path(filename).name, foreground="black")
            self.update_process_button_state()
    
    def select_style(self):
        """Select style reference image file"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Style Reference Image (Scene Background)",
            filetypes=filetypes
        )
        
        if filename:
            self.style_path = filename
            self.style_label.config(text=Path(filename).name, foreground="black")
            self.update_process_button_state()
    
    def select_output_dir(self):
        """Select output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_var.set(directory)
    
    def update_process_button_state(self):
        """Update the process button state based on inputs"""
        if self.selfie_path and self.style_path:
            try:
                secure_storage = SecureStorage()
                api_key = secure_storage.load_api_key("Qwen-VL-Max (Alibaba Cloud)")
                if api_key:
                    self.process_button.config(state=tk.NORMAL)
                    return
            except:
                pass
        
        self.process_button.config(state=tk.DISABLED)
    
    def setup_api_key(self):
        """Setup API key dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Setup API Key")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="OpenAI API Key Setup", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        ttk.Label(frame, text="To use the style transfer feature, you need a Qwen-VL-Max API key.").pack(pady=(0, 5))
        ttk.Label(frame, text="Get one from: https://dashscope.console.aliyun.com/").pack(pady=(0, 20))
        
        ttk.Label(frame, text="Enter your API key:").pack(anchor=tk.W)
        key_var = tk.StringVar()
        key_entry = ttk.Entry(frame, textvariable=key_var, show="*", width=50)
        key_entry.pack(pady=(5, 20), fill=tk.X)
        key_entry.focus()
        
        def save_key():
            api_key = key_var.get().strip()
            if not api_key:
                messagebox.showerror("Error", "Please enter an API key.")
                return
            
            try:
                secure_storage = SecureStorage()
                secure_storage.save_api_key("Qwen-VL-Max (Alibaba Cloud)", api_key)
                messagebox.showinfo("Success", "API key saved successfully!")
                dialog.destroy()
                self.check_api_key()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save API key: {e}")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(10, 0))
        
        ttk.Button(button_frame, text="Save", command=save_key).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        # Bind Enter key to save
        dialog.bind('<Return>', lambda e: save_key())
    
    def start_process(self):
        """Start the style transfer process in a separate thread"""
        if not self.selfie_path or not self.style_path:
            messagebox.showerror("Error", "Please select both selfie and style reference images.")
            return
        
        # Create output directory
        output_dir = self.output_var.get()
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create output directory: {e}")
            return
        
        # Disable button and start progress
        self.process_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="Processing...", foreground="blue")
        
        # Clear results area
        self.results_text.delete(1.0, tk.END)
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.process_style_transfer)
        thread.daemon = True
        thread.start()
    
    def process_style_transfer(self):
        """Process style transfer (runs in separate thread)"""
        try:
            # Initialize processor
            if not self.processor:
                self.processor = StyleTransferProcessor()
            
            analyze_only = self.analyze_only_var.get()
            output_dir = self.output_var.get()
            
            if analyze_only:
                # Analysis only mode
                self.update_status("Analyzing selfie...")
                selfie_analysis = self.processor.analyze_selfie(self.selfie_path)
                
                self.update_status("Analyzing style reference...")
                style_analysis = self.processor.analyze_style_reference(self.style_path)
                
                self.update_status("Generating style transfer prompt...")
                transfer_prompt = self.processor.generate_style_transfer_prompt(
                    selfie_analysis, style_analysis
                )
                
                # Display results
                self.display_analysis_results(selfie_analysis, style_analysis, transfer_prompt)
                
                # Save analyses
                timestamp = int(datetime.now().timestamp())
                
                selfie_analysis_path = os.path.join(output_dir, f"selfie_analysis_{timestamp}.json")
                with open(selfie_analysis_path, 'w', encoding='utf-8') as f:
                    json.dump(selfie_analysis, f, indent=2, ensure_ascii=False)
                
                style_analysis_path = os.path.join(output_dir, f"style_analysis_{timestamp}.json")
                with open(style_analysis_path, 'w', encoding='utf-8') as f:
                    json.dump(style_analysis, f, indent=2, ensure_ascii=False)
                
                prompt_path = os.path.join(output_dir, f"transfer_prompt_{timestamp}.txt")
                with open(prompt_path, 'w', encoding='utf-8') as f:
                    f.write(transfer_prompt)
                
                self.update_status("Analysis complete! Files saved to output directory.")
                
            else:
                # Full workflow mode
                self.update_status("Running complete style transfer workflow...")
                
                results = self.processor.process_style_transfer_workflow(
                    self.selfie_path,
                    self.style_path,
                    output_dir
                )
                
                # Display results
                self.display_workflow_results(results)
                
                if results['generation_success']:
                    self.update_status(f"Style transfer complete! Output: {Path(results['output_image']).name}")
                else:
                    self.update_status("Style transfer completed with issues. Check results.")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "red")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Style transfer failed: {e}"))
        
        finally:
            # Re-enable button and stop progress
            self.root.after(0, self.finish_process)
    
    def update_status(self, message, color="blue"):
        """Update status label (thread-safe)"""
        self.root.after(0, lambda: self.status_label.config(text=message, foreground=color))
    
    def display_analysis_results(self, selfie_analysis, style_analysis, transfer_prompt):
        """Display analysis results in the results area"""
        def update_results():
            self.results_text.delete(1.0, tk.END)
            
            # Selfie analysis
            self.results_text.insert(tk.END, "📸 SELFIE ANALYSIS\n", "header")
            self.results_text.insert(tk.END, "=" * 50 + "\n\n")
            
            person_details = selfie_analysis.get('person_details', {})
            if person_details.get('pose'):
                self.results_text.insert(tk.END, f"👤 Pose: {person_details['pose'][:100]}...\n")
            if person_details.get('clothing'):
                self.results_text.insert(tk.END, f"👕 Clothing: {person_details['clothing'][:100]}...\n")
            
            background_info = selfie_analysis.get('background_info', {})
            if background_info.get('description'):
                self.results_text.insert(tk.END, f"🖼️ Background: {background_info['description'][:100]}...\n")
            
            # Style analysis
            self.results_text.insert(tk.END, "\n🎨 STYLE REFERENCE ANALYSIS\n", "header")
            self.results_text.insert(tk.END, "=" * 50 + "\n\n")
            
            scene_details = style_analysis.get('scene_description', {})
            if scene_details.get('environment'):
                self.results_text.insert(tk.END, f"🌍 Environment: {scene_details['environment'][:100]}...\n")
            
            color_palette = style_analysis.get('color_palette', {})
            if color_palette.get('dominant_colors'):
                self.results_text.insert(tk.END, f"🎨 Colors: {color_palette['dominant_colors'][:100]}...\n")
            
            mood_info = style_analysis.get('mood_atmosphere', {})
            if mood_info.get('atmosphere'):
                self.results_text.insert(tk.END, f"✨ Mood: {mood_info['atmosphere'][:100]}...\n")
            
            # Generated prompt
            self.results_text.insert(tk.END, "\n✍️ GENERATED STYLE TRANSFER PROMPT\n", "header")
            self.results_text.insert(tk.END, "=" * 50 + "\n\n")
            self.results_text.insert(tk.END, transfer_prompt)
            
            # Configure tags
            self.results_text.tag_config("header", font=("Arial", 12, "bold"))
        
        self.root.after(0, update_results)
    
    def display_workflow_results(self, results):
        """Display workflow results in the results area"""
        def update_results():
            self.results_text.delete(1.0, tk.END)
            
            self.results_text.insert(tk.END, "🎨 STYLE TRANSFER WORKFLOW RESULTS\n", "header")
            self.results_text.insert(tk.END, "=" * 50 + "\n\n")
            
            self.results_text.insert(tk.END, f"✅ Success: {results['generation_success']}\n")
            if results.get('output_image'):
                self.results_text.insert(tk.END, f"📁 Output Image: {Path(results['output_image']).name}\n")
            
            # Quick analysis summary
            selfie_analysis = results['analyses']['selfie']
            style_analysis = results['analyses']['style_reference']
            
            self.results_text.insert(tk.END, "\n📊 Quick Summary:\n")
            
            person_details = selfie_analysis.get('person_details', {})
            if person_details.get('pose'):
                self.results_text.insert(tk.END, f"👤 Pose: {person_details['pose'][:80]}...\n")
            
            scene_details = style_analysis.get('scene_description', {})
            if scene_details.get('environment'):
                self.results_text.insert(tk.END, f"🌍 Scene: {scene_details['environment'][:80]}...\n")
            
            # Generated prompt preview
            self.results_text.insert(tk.END, "\n✍️ Prompt Preview:\n")
            prompt_preview = results['generated_prompt'][:300] + "..." if len(results['generated_prompt']) > 300 else results['generated_prompt']
            self.results_text.insert(tk.END, prompt_preview)
            
            # Configure tags
            self.results_text.tag_config("header", font=("Arial", 12, "bold"))
        
        self.root.after(0, update_results)
    
    def finish_process(self):
        """Finish the process (re-enable UI)"""
        self.progress.stop()
        self.process_button.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = StyleTransferGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
