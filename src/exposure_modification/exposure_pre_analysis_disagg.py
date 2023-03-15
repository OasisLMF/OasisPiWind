import pandas as pd

class ExposurePreAnalysis:
    """
    Example of custum module called by oasislmf/model_preparation/ExposurePreAnalysis.py

    This module splits aggregate location records (NumberOfBuildings>1) where OccupancyCode=1000 (unknown) into many rows and proportionally
    allocates TIV and NumberOfBuildings to specific OccupancyCode's, where this data exists in the reference dataset (OEDLocBuildEnv) representing 
    the built environment. OccupancyCodes are matched to locations on the PostalCode field.
    
    This represents a partial disaggregation of aggregate locations to the attributes that are important in the model (just OccupancyCode for PiWind) and then
    the partially disaggregated risks can be split equally into individual buildings during the model execution.

    This routine enables the model provider to augment the source location data with information that is important for the model (to make the best choice of
    vulnerability functions) using known built environment data in a standard format, without performing a full disaggregation to individual building level, 
    pre-analysis. 
    """

    def __init__(self, exposure_data, exposure_pre_analysis_setting, **kwargs):
        self.exposure_data = exposure_data
        self.exposure_pre_analysis_setting = exposure_pre_analysis_setting

    def run(self):
        """example of adding a new column to exposure_data.location.dataframe"""
        panda_df = self.exposure_data.location.dataframe
        df_built_env = pd.read_csv('src/exposure_modification/OEDLocBuiltEnv.csv')

    # Fill source location file defaults for disaggregation

    # Make sure IsAggregate is there and filled (not mandatory), otherwise assume IsAggregate = 0
        if not ('IsAggregate' in panda_df.columns):
             panda_df['IsAggregate'] = 0
             panda_df['IsAggregate'].fillna(0, inplace=True)

        # Make sure NumberOfBuildings is there and filled (not mandatory), otherwise assume NumberOfBuildings = 1
        if not ('NumberOfBuildings' in panda_df.columns):
             panda_df['NumberOfBuildings'] = 1
             panda_df['NumberOfBuildings'].fillna(1, inplace=True)

        # Make sure OccupancyCode is there and filled (not mandatory), otherwise assume OccupancyCode = 1000 (unknown)
        if not ('OccupancyCode' in panda_df.columns):
             panda_df['OccupancyCode'] = 1000
             panda_df['OccupancyCode'].fillna(1000, inplace=True)

        # Make sure ConstructionCode is there and filled (not mandatory), otherwise assume ConstructionCode = 5000 (unknown)
        if not ('ConstructionCode' in panda_df.columns):
             panda_df['ConstructionCode'] = 5000
             panda_df['ConstructionCode'].fillna(5000, inplace=True)

        # Specify condition for disaggregation (known PostalCode, unknown Occupancy, NumberOfBuildings > 1)

        bool_disagg = ((panda_df['OccupancyCode'] == 1000) & (panda_df['NumberOfBuildings'] > 1) & (panda_df['PostalCode'].notna()))
        
        # Filter locations that need disaggregation
        df_source_loc_disagg = panda_df[bool_disagg]

        # Filter locations that don't need disaggregation
        df_source_loc_no_disagg = panda_df[~bool_disagg]

        # merge locations that need disaggregation with built environment file on PostalCode
        df_merge_groupsum_pc_occ_1 = pd.merge(df_source_loc_disagg,df_built_env,on='PostalCode').groupby(['PostalCode','OccupancyCode_y'], as_index=False).agg({'BuildingTIV_y':'sum','ContentsTIV_y':'sum','OtherTIV_y':'sum','BITIV_y':'sum','NumberOfBuildings_y':'sum'})
        df_merge_groupsum_pc_occ_1.rename(columns={'OccupancyCode_y': 'OccupancyCode_new', 'BuildingTIV_y': 'BuildingTIV_Occ', 'ContentsTIV_y': 'ContentsTIV_Occ', 'OtherTIV_y': 'OtherTIV_Occ', 'BITIV_y': 'BITIV_Occ', 'NumberOfBuildings_y': 'NumberOfBuildings_Occ'}, inplace=True)

        # group merged locations by PostalCode and sum values across OccupancyCode
        df_groupsum_pc_2 = df_merge_groupsum_pc_occ_1.groupby(['PostalCode']).agg({'BuildingTIV_Occ':'sum','ContentsTIV_Occ':'sum','OtherTIV_Occ':'sum','BITIV_Occ':'sum','NumberOfBuildings_Occ':'sum'})
        df_groupsum_pc_2.rename(columns={'BuildingTIV_Occ': 'BuildingTIV_Tot', 'ContentsTIV_Occ': 'ContentsTIV_Tot', 'OtherTIV_Occ': 'OtherTIV_Tot', 'BITIV_Occ': 'BITIV_Tot', 'NumberOfBuildings_Occ': 'NumberOfBuildings_Tot'}, inplace=True)

        # Merge df 1 and df 2 back together so that weights can be calculated by OccupancyCode and PostalCode
        df_merge_3 = pd.merge(df_merge_groupsum_pc_occ_1,df_groupsum_pc_2,on='PostalCode',how="outer")

        # Calculate the weights for TIV and Number of Buildings disaggregation by OccupancyCode within PostalCode
        df_merge_3['BuildingTIV_weight']= df_merge_3['BuildingTIV_Occ'] /  df_merge_3['BuildingTIV_Tot']
        df_merge_3['ContentsTIV_weight']= df_merge_3['ContentsTIV_Occ'] /  df_merge_3['ContentsTIV_Tot']
        df_merge_3['BITIV_weight']= df_merge_3['BITIV_Occ'] /  df_merge_3['BITIV_Tot']
        df_merge_3['NumberOfBuildings_weight']= df_merge_3['NumberOfBuildings_Occ'] /  df_merge_3['NumberOfBuildings_Tot']

        # Disaggregate the TIV and Number of Buildings using the weights
        df_source_disagg = pd.merge(df_source_loc_disagg,df_merge_3,on='PostalCode')
        df_source_disagg['BuildingTIV_new']= df_source_disagg['BuildingTIV'] * df_source_disagg['BuildingTIV_weight']
        df_source_disagg['ContentsTIV_new']= df_source_disagg['ContentsTIV'] * df_source_disagg['ContentsTIV_weight']
        df_source_disagg['BITIV_new']= df_source_disagg['BITIV'] * df_source_disagg['BITIV_weight']
        df_source_disagg['NumberOfBuildings_new']= df_source_disagg['NumberOfBuildings'] * df_source_disagg['NumberOfBuildings_weight']
        df_source_disagg['NumberOfBuildings_new']= df_source_disagg['NumberOfBuildings_new'].round(decimals=0).astype(int) # ! Need to make sure sum adds up to original NumberOfBuildings

        # Tidy up and set the original OED field values to use the calculated values. Use FlexiLoc fields for the original values which we don't want to use for disaggregated locations.
        df_source_disagg = df_source_disagg.drop(columns=['BuildingTIV_Occ','ContentsTIV_Occ','OtherTIV_Occ', 'BITIV_Occ', 'NumberOfBuildings_Occ',
         'BuildingTIV_Tot', 'ContentsTIV_Tot', 'OtherTIV_Tot', 'BITIV_Tot', 'NumberOfBuildings_Tot', 'BuildingTIV_weight', 'ContentsTIV_weight',
         'BITIV_weight', 'NumberOfBuildings_weight',])
        df_source_disagg.rename(columns={'OccupancyCode': 'FlexiLocOccupancyCodeOrig', 'BuildingTIV': 'FlexiLocBuildingTIVOrig', 'ContentsTIV': 'FlexiLocContentsTIVOrig', 'BITIV': 'FlexiLocBITIVOrig', 'NumberOfBuildings': 'FlexiLocNumberOfBuildingsOrig'}, inplace=True)
        df_source_disagg.rename(columns={'OccupancyCode_new': 'OccupancyCode', 'BuildingTIV_new': 'BuildingTIV', 'ContentsTIV_new': 'ContentsTIV',  'BITIV_new': 'BITIV', 'NumberOfBuildings_new': 'NumberOfBuildings'}, inplace=True)

        # Align the locations that haven't been disaggregated to the new OED location output file. We keep the original TIVs and NumberOfBuildings unchanged for these.
        # Have to make a copy here, to avoid python warnings about inplace replacement / renaming of fields for a slice of a dataframe.
        df_copy = df_source_loc_no_disagg.copy() 
        df_copy.rename(columns={'OccupancyCode': 'FlexiLocOccupancyCodeOrig', 'BuildingTIV': 'FlexiLocBuildingTIVOrig', 'ContentsTIV': 'FlexiLocContentsTIVOrig', 'BITIV': 'FlexiLocBITIVOrig', 'NumberOfBuildings': 'FlexiLocNumberOfBuildingsOrig'}, inplace=True)
        df_copy['OccupancyCode']=df_copy['FlexiLocOccupancyCodeOrig']
        df_copy['BuildingTIV']=df_copy['FlexiLocBuildingTIVOrig']
        df_copy['ContentsTIV']=df_copy['FlexiLocContentsTIVOrig']
        df_copy['BITIV']=df_copy['FlexiLocBITIVOrig']
        df_copy['NumberOfBuildings']=df_copy['FlexiLocNumberOfBuildingsOrig']

        # Vertical merge the disaggregated locations with the locations that did not need disaggregation
        df_output = pd.concat([df_copy, df_source_disagg], axis=0,ignore_index=True,join='inner')

        # df_output to be written out to location.csv
        panda_df = df_output.copy()
