
#file path and attribute names of first state
Dream3d0 = {'path':'/home/fyshen13/Downloads/AngFiles_Anneal0_Output/Segment_15_2deg_27.dream3d',
        'ID':'FeatureIds',
        'IPF':'IPFColor',
        'Mask':'Mask',
        'Euler':'EulerAngles',
#        'AvgEuler':'AvgEulerAngles',
        'Centroids':'Centroids',
        'Confidence':'Confidence Index'}

#file path and attribute names of second state
Dream3d1 = {'path':'/home/fyshen13/Downloads/AngFiles_Anneal1_Output/Segment_match_2deg_27.dream3d',
        'ID':'FeatureIds',
        'IPF':'IPFColor',
        'Mask':'Mask',
        'Euler':'EulerAngles',
#        'AvgEuler':'AvgEulerAngles',
        'Centroids':'Centroids',
        'Confidence':'Confidence Index'}

#feature IDs of unmatched grains or any grain IDs that you want to show
interestidfname='nomatchgrainIDs.txt'

#label names that you want to record
label = {'outputfilename':'GrainMatch_Qt_res.pickle',
        'labels':["low confidence","match","mis-reconstructed","new grain"]}

#zgap is the distance (in um) between layers
zgap = 3
