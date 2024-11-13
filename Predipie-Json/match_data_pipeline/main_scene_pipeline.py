from match_pipeline import MatchDataPipeline
from match_pipeline_stats import MatchDataPipelineWithStats
from match_pipeline_odds import MatchDataPipelineWithOdds
from match_pipeline_recent_form import MatchDataPipelineWithRecentForm  

def run_all_pipelines(api_url):
    """Run all pipelines to generate outputs for scene2, scene3, scene4, and scene5 in separate folders."""
    
    # اجرای خط لوله برای scene2
    print("Processing Scene 2...")
    scene2_pipeline = MatchDataPipeline(api_url, folder_name='scene2')
    scene2_pipeline.process()

    # اجرای خط لوله برای scene3
    print("Processing Scene 3...")
    scene3_pipeline = MatchDataPipelineWithStats(api_url, folder_name='scene3')
    scene3_pipeline.process()

    # اجرای خط لوله برای scene4
    print("Processing Scene 4...")
    scene4_pipeline = MatchDataPipelineWithOdds(api_url, folder_name='scene4')
    scene4_pipeline.process()

    # اجرای خط لوله برای scene5
    print("Processing Scene 5...")
    scene5_pipeline = MatchDataPipelineWithRecentForm(api_url, folder_name='scene5')
    scene5_pipeline.process()

if __name__ == "__main__":
    api_url = 'https://dataprovider.predipie.com/api/v1/ai/test/'  
    run_all_pipelines(api_url)
