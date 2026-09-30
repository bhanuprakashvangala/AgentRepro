"""
Image Classifier using Pre-trained ResNet50
Classifies images from a folder using ImageNet categories
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import json
import sys
from pathlib import Path


class ImageClassifier:
    def __init__(self, model_name='resnet50'):
        """
        Initialize the image classifier with a pre-trained model

        Args:
            model_name: Name of the model to use ('resnet50', 'resnet101', 'vgg16', 'vgg19')
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")

        # Load pre-trained model
        print(f"Loading {model_name} model...")
        if model_name == 'resnet50':
            self.model = models.resnet50(pretrained=True)
        elif model_name == 'resnet101':
            self.model = models.resnet101(pretrained=True)
        elif model_name == 'vgg16':
            self.model = models.vgg16(pretrained=True)
        elif model_name == 'vgg19':
            self.model = models.vgg19(pretrained=True)
        else:
            raise ValueError(f"Unsupported model: {model_name}")

        self.model = self.model.to(self.device)
        self.model.eval()

        # Define image preprocessing pipeline
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        # Load ImageNet class labels
        self.class_labels = self._load_imagenet_labels()

    def _load_imagenet_labels(self):
        """Load ImageNet class labels"""
        # ImageNet class index to human-readable labels
        # Using a subset of common classes for demonstration
        labels = {}
        try:
            # Try to load from URL (requires internet)
            import urllib.request
            url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
            with urllib.request.urlopen(url, timeout=10) as response:
                labels_list = json.loads(response.read().decode())
                labels = {i: label for i, label in enumerate(labels_list)}
        except Exception as e:
            print(f"Warning: Could not load labels from internet: {e}")
            print("Using generic labels instead.")
            # Fallback to generic labels
            labels = {i: f"class_{i}" for i in range(1000)}

        return labels

    def predict_image(self, image_path, top_k=5):
        """
        Predict the class of a single image

        Args:
            image_path: Path to the image file
            top_k: Number of top predictions to return

        Returns:
            List of tuples (class_name, confidence_score)
        """
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            input_tensor = self.preprocess(image)
            input_batch = input_tensor.unsqueeze(0).to(self.device)

            # Make prediction
            with torch.no_grad():
                output = self.model(input_batch)

            # Apply softmax to get probabilities
            probabilities = torch.nn.functional.softmax(output[0], dim=0)

            # Get top-k predictions
            top_probs, top_indices = torch.topk(probabilities, top_k)

            # Format results
            results = []
            for prob, idx in zip(top_probs, top_indices):
                class_name = self.class_labels.get(idx.item(), f"class_{idx.item()}")
                confidence = prob.item()
                results.append((class_name, confidence))

            return results

        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return []

    def classify_folder(self, folder_path, top_k=5, output_file='predictions.txt'):
        """
        Classify all images in a folder

        Args:
            folder_path: Path to folder containing images
            top_k: Number of top predictions per image
            output_file: Path to output file for results
        """
        # Supported image extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}

        folder = Path(folder_path)
        if not folder.exists():
            print(f"Error: Folder '{folder_path}' does not exist")
            return

        # Find all image files
        image_files = [
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        if not image_files:
            print(f"No image files found in '{folder_path}'")
            return

        print(f"\nFound {len(image_files)} images to classify\n")
        print("=" * 80)

        # Process each image
        results = {}
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] Processing: {image_path.name}")
            predictions = self.predict_image(image_path, top_k)

            if predictions:
                results[str(image_path)] = predictions
                print(f"\nTop {top_k} predictions:")
                for rank, (class_name, confidence) in enumerate(predictions, 1):
                    print(f"  {rank}. {class_name:<30} (confidence: {confidence:.4f} = {confidence*100:.2f}%)")

            print("-" * 80)

        # Save results to file
        self._save_results(results, output_file)
        print(f"\n✓ Results saved to: {output_file}")

    def _save_results(self, results, output_file):
        """Save classification results to a text file"""
        with open(output_file, 'w') as f:
            f.write("IMAGE CLASSIFICATION RESULTS\n")
            f.write("=" * 80 + "\n\n")

            for image_path, predictions in results.items():
                f.write(f"Image: {image_path}\n")
                f.write("-" * 80 + "\n")
                for rank, (class_name, confidence) in enumerate(predictions, 1):
                    f.write(f"  {rank}. {class_name:<30} (confidence: {confidence:.4f} = {confidence*100:.2f}%)\n")
                f.write("\n")


def main():
    """Main function to run the image classifier"""
    import argparse

    parser = argparse.ArgumentParser(description='Classify images using pre-trained models')
    parser.add_argument('folder_path', type=str, help='Path to folder containing images')
    parser.add_argument('--model', type=str, default='resnet50',
                        choices=['resnet50', 'resnet101', 'vgg16', 'vgg19'],
                        help='Pre-trained model to use (default: resnet50)')
    parser.add_argument('--top-k', type=int, default=5,
                        help='Number of top predictions to show (default: 5)')
    parser.add_argument('--output', type=str, default='predictions.txt',
                        help='Output file for results (default: predictions.txt)')

    args = parser.parse_args()

    # Create classifier and process images
    classifier = ImageClassifier(model_name=args.model)
    classifier.classify_folder(args.folder_path, top_k=args.top_k, output_file=args.output)


if __name__ == '__main__':
    main()
