import sys
import os

project_path = '/'.join(__file__.split('/')[:-1])+'/'
sys.path.append(project_path)

import analysis.analysis_plots as ap

def main( file_date ):
    simulation_settings, game_metadata, turn_df = ap.get_all_game_pkls(file_date)
    ap.set_image_output_path(file_date)

    turn_df['colors'] = ap.player_color_series(turn_df)

    ap.gen_vp_avg_plot(
        simulation_settings,
        game_metadata,
        turn_df,
        True
    )

    ap.gen_vp_sum_plot(
        simulation_settings,
        game_metadata,
        turn_df,
        True
    )

    ap.gen_first_last_avg_plot(
        simulation_settings,
        game_metadata,
        turn_df,
        output_image=True,
        n_games=5,
        min_count=0
    )

    ap.gen_cum_wins(
        simulation_settings,
        game_metadata,
        turn_df,
        True
    )

if ( __name__=='__main__' ):
    file_date = ap.get_latest_game_file()
    if ( len(sys.argv) > 1 ):
        file_date = sys.argv[1]
    print("Using file date: {}".format(file_date))
    main(file_date)
