import os
import sys
import logging
from datetime import datetime
import json
import torch
import gc
from data_preparation import DataPreparator
from models import ModelManager
from evaluation import Evaluator

def setup_logging():
    """Setup logging configuration"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/tourism_qa_{timestamp}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def save_results(results, model_name, output_dir):
    """Save evaluation results to JSON file"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/results_{model_name}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    logging.info(f"Results saved to {filename}")

def cleanup_gpu():
    """Clean up GPU memory"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()

def main():
    setup_logging()
    logging.info("Starting Tourism QA System")
    
    try:
        # Initialize components
        data_prep = DataPreparator()
        model_manager = ModelManager()
        evaluator = Evaluator()
        
        # Create output directory
        output_dir = './output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Prepare data
        logging.info("Starting data preparation...")
        csv_path = 'tourism_guides.csv'
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Tourism guides file not found at {csv_path}")
        
        train_data, val_data, test_data = data_prep.prepare_tourism_data(
            csv_path,
            test_size=0.2,
            val_size=0.1
        )
        
        if train_data is None or val_data is None or test_data is None:
            raise ValueError("Data preparation failed - check the data format and content")
        
        logging.info(f"Data split sizes - Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
        
        # Initialize models
        logging.info("Initializing models...")
        model_manager.initialize_models()
        
        if not model_manager.models:
            raise ValueError("No models were successfully loaded - check model configurations")
        
        # Train and evaluate each model
        results = {}
        for model_name, model in model_manager.models.items():
            try:
                logging.info(f"\nProcessing model: {model_name}")
                logging.info("=" * 50)
                model_output_dir = os.path.join(output_dir, model_name)
                
                # Training phase
                logging.info(f"Training {model_name}...")
                trainer = model_manager.train_model(
                    model_name,
                    train_data,
                    val_data,
                    model_output_dir
                )
                
                if trainer is None:
                    logging.error(f"Training failed for {model_name} - skipping evaluation")
                    continue
                
                # Clean up GPU memory after training
                cleanup_gpu()
                
                # Evaluation phase
                logging.info(f"Evaluating {model_name}...")
                model_results, detailed_results = evaluator.evaluate_model(
                    model_manager.models[model_name],
                    model_manager.tokenizers[model_name],
                    test_data
                )
                
                results[model_name] = {
                    'metrics': model_results,
                    'detailed_results': detailed_results
                }
                
                # Save individual model results
                save_results(results[model_name], model_name, model_output_dir)
                
                # Print current model results
                logging.info(f"\nResults for {model_name}:")
                for metric, score in model_results.items():
                    logging.info(f"{metric}: {score:.4f}")
                
                # Clean up GPU memory after evaluation
                cleanup_gpu()
                
            except Exception as e:
                logging.error(f"Error processing model {model_name}: {str(e)}")
                continue
        
        # Print comparative results
        if results:
            logging.info("\nComparative Model Results:")
            logging.info("=" * 50)
            
            # Create a formatted table header
            metrics = next(iter(results.values()))['metrics'].keys()
            header = "Model".ljust(15) + " | " + " | ".join(str(m).ljust(10) for m in metrics)
            logging.info(header)
            logging.info("-" * len(header))
            
            # Print each model's results
            for model_name, model_results in results.items():
                scores = [f"{score:.4f}".ljust(10) for score in model_results['metrics'].values()]
                logging.info(f"{model_name.ljust(15)} | {' | '.join(scores)}")
        else:
            logging.warning("No results were generated - all models failed to process")
        
        # Clean up
        model_manager.cleanup()
        logging.info("\nProcessing completed successfully")
        
    except Exception as e:
        logging.error(f"Critical error in main execution: {str(e)}")
        raise
    
    finally:
        cleanup_gpu()

if __name__ == "__main__":
    main()