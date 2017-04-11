
------------------------------------------
--Catrisks MEEQ
------------------------------------------
Declare	@SupplierId int = (Select ISNULL(Max(SupplierId),0) + 1 From Supplier)
Declare	@ModelFamilyId int = (Select ISNULL(Max(ModelFamilyId),0) + 1 From ModelFamily)
Declare	@ModelId int = (Select ISNULL(Max(ModelId),0) + 1 From Model)
Declare	@ServiceId int = (Select ISNULL(Max(ServiceId),0) + 1 From Service)
Declare	@OasisSystemId int = (Select ISNULL(Max(OasisSystemId),0) + 1 From OasisSystem)
Declare	@OasisSystemServiceId int = (Select ISNULL(Max(OasisSystemServiceId),0) + 1 From OasisSystemService)
Declare	@ModelResourceId int = (Select ISNULL(Max(ModelResourceId),0) From ModelResource)

Declare	@ModelLicenseId int = (Select ISNULL(Max(ModelLicenseId),0) + 1 From ModelLicense)
Declare	@OasisUserId int = (Select ISNULL(Max(OasisUserId),0) + 1 From OasisUser) --to be fixed
Declare	@UserLicenseId int = (Select ISNULL(Max(UserLicenseId),0) + 1 From UserLicense)

Declare	@ResourceId int = (Select ISNULL(Max(ResourceId),0) + 1 From [Resource])
Declare	@FileId int = (Select ISNULL(Max(FileId),0) + 1 From [File])
Declare	@TransformId int = (Select ISNULL(Max(TransformId),0) + 1 From [Transform])
Declare	@FileResourceId int = (Select ISNULL(Max(FileResourceId),0) + 1 From [FileResource])
Declare @ProfileResourceId int = (Select ISNULL(Max(ProfileResourceId),0) + 1 From [ProfileResource])
Declare @ProfileId int = (Select ISNULL(Max(ProfileId),0) + 1 From [Profile])
Declare @ProfileElementId int = (Select ISNULL(Max(ProfileElementId),0) From [ProfileElement])
Declare @ProfileValueDetailID int = (Select ISNULL(Max(ProfileValueDetailID),0) + 1 From [ProfileValueDetail])

--Supplier
INSERT [dbo].[Supplier] ([SupplierID], [SupplierName], [SupplierDesc], [SupplierLegalName], [SupplierAddress], [SupplierPostcode], [SupplierTelNo], [Deleted]) 
		VALUES (@SupplierId,N'Catrisks',N'Catrisks',N'Catrisks',N'',N'',N'',0)

--ModelFamily
INSERT [dbo].[ModelFamily] ([ModelFamilyID], [ModelFamilyName], [SupplierID]) 
		VALUES (@ModelFamilyId, N'MEEQ', @SupplierId)

--Model
INSERT [dbo].[Model] ([ModelID], [ModelName], [ModelFamilyID], [ModelDescription], [VersionRef], [ReleaseDate], [Contact], [ModelTypeId], [Deleted]) 
		VALUES (@ModelId, N'Catrisks MEEQ', @ModelFamilyId, N'MEEQ Model', N'1.0', N'Nov 2016', N'Mohammad Zolfaghari', 1, 0)

--Service
INSERT [dbo].[Service] ([ServiceID], [ServiceName], [ServiceDesc], [ServiceTypeId], [ModelId]) 
		VALUES (@ServiceId, N'Catrisks Oasis', N'Catrisks Oasis Mid Tier', 1, @ModelId)
INSERT [dbo].[Service] ([ServiceID], [ServiceName], [ServiceDesc], [ServiceTypeId], [ModelId]) 
		VALUES (@ServiceId+1, N'Catrisks API', N'Catrisks Oasis Key Lookup Service', 2, @ModelId)

--OasisSystem
INSERT [dbo].[OasisSystem] ([OasisSystemID], [OasisSystemName], [OasisSystemDescription], [url], [Port], [SysConfigID]) 
		VALUES (@OasisSystemId, N'Catrisks Oasis Mid Tier', N'Catrisks Oasis Mid Tier', N'%OASIS_API_IP%', %OASIS_API_PORT%, 4)
INSERT [dbo].[OasisSystem] ([OasisSystemID], [OasisSystemName], [OasisSystemDescription], [url], [Port], [SysConfigID]) 
		VALUES (@OasisSystemId+1, N'Catrisks API', N'Catrisks Keys Service', N'%CATRISKS_KEYS_IP%:%CATRISKS_KEYS_PORT%/catrisks/meeq/1.0/get_keys', NULL, NULL)

--OasisSystemService
INSERT [dbo].[OasisSystemService] ([OasisSystemServiceID], [OasisSystemID], [ServiceID]) 
		VALUES (@OasisSystemServiceId, @OasisSystemId, @ServiceId)
INSERT [dbo].[OasisSystemService] ([OasisSystemServiceID], [OasisSystemID], [ServiceID]) 
		VALUES (@OasisSystemServiceId+1, @OasisSystemId+1, @ServiceId+1)

--ModelResource
Create Table #ModelResource
		(
		ModelResourceId int identity,
		ModelResourceName nvarchar(255),
		ResourceTypeID int,
		OasisSystemID int,
		ModelID int,
		ModelResourceValue nvarchar(255),
		)

INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'model_file_extension', 305, @OasisSystemID+1, @ModelID, N'csv')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'Catrisks API', 1000, @OasisSystemID+1, @ModelID, N'')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'ModelGroupField', 300, @OasisSystemID, @ModelID, N'AreaPerilID')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'module_supplier_id', 301, @OasisSystemID, @ModelID, N'Catrisks')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'model_version_id', 302, @OasisSystemID, @ModelID, N'MEEQ')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'peril_quake', 1001, @OasisSystemId, @ModelID, N'checkbox')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'event_set', 1001, @OasisSystemId, @ModelID, N'dropdown')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'event_occurance_id', 1001, @OasisSystemId, @ModelID, N'dropdown')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'event_set', 303, @OasisSystemId, @ModelID, N'P')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'event_occurance_id', 304, @OasisSystemId, @ModelID, N'1')


INSERT	[dbo].[ModelResource] ([ModelResourceID], [ModelResourceName], [ResourceTypeID], [OasisSystemID], [ModelID], [ModelResourceValue])
SELECT	[ModelResourceID] + @ModelResourceId as [ModelResourceID], 
		[ModelResourceName], 
		[ResourceTypeID], 
		[OasisSystemID], 
		[ModelID], 
		[ModelResourceValue]
FROM	#ModelResource

DROP TABLE #ModelResource

--ModelLicense
INSERT [dbo].[ModelLicense] ([ModelLicenseID], [ModelID], [CompanyID], [ModelLicenseName], [ModelVersionDescription], [LicenseStartDate], [LicenseEndDate], [LicenseType], [LicenseContractRef]) 
		VALUES (@ModelLicenseId, @ModelId, 1, N'Catrisks MEEQ Model License', N'Catrisks Model License', '01/01/1900', '12/31/9999', 'Dummy License', 'MZ')

--OasisUser
INSERT [dbo].[OasisUser] ([OasisUserID], [OasisUserName], [ModelLicenseID], [OasisSystemID], [SystemLogin], [SystemPassword], [Django Login], [Django Password]) 
		VALUES (@OasisUserId, N'OasisUserCatrisks', @ModelLicenseId, @OasisSystemId, N'Root', N'Password', N'', N'')

--UserLicense
INSERT [dbo].[UserLicense] ([UserLicenseId], [BFEUserID], [OasisUserID]) VALUES (@UserLicenseId, 1, @OasisUserId)


---------------------------------------------------------
--Params
Set	@ResourceId = (Select ISNULL(Max(ResourceId),0) + 1 From [Resource])
Set	@FileId = (Select ISNULL(Max(FileId),0) + 1 From [File])
Set	@FileResourceId = (Select ISNULL(Max(FileId),0) + 1 From [FileResource])
Set	@TransformId = (Select ISNULL(Max(TransformId),0) + 1 From [Transform])

Declare @FromLocXSDResourceID int
Declare @ToLocXSDResourceID int
Declare @XSLTLocResourceID int
Declare @FromAccXSDResourceID int
Declare @ToAccXSDResourceID int
Declare @XSLTAccResourceID int
Declare @LocProfileResourceID int
Declare @AccProfileResourceID int

Declare @FromLocXSDFileID int
Declare @ToLocXSDFileID int
Declare @XSLTLocFileID int
Declare @FromAccXSDFileID int
Declare @ToAccXSDFileID int
Declare @XSLTAccFileID int

Declare @FromLocXSDFileResourceID int
Declare @ToLocXSDFileResourceID int
Declare @XSLTLocFileResourceID int
Declare @FromAccXSDFileResourceID int
Declare @ToAccXSDFileResourceID int
Declare @XSLTAccFileResourceID int

Declare @LocProfileId int
Declare @AccProfileId int  

Declare @LocPofileResourceID int
Declare @AccPofileResourceID int

-------------source to canonical------------------------

Set		@FromLocXSDResourceID	= @ResourceId
Set		@ToLocXSDResourceID		= @ResourceId +1
Set		@XSLTLocResourceID		= @ResourceId +2
Set		@FromAccXSDResourceID	= @ResourceId +3
Set		@ToAccXSDResourceID		= @ResourceId +4
Set		@XSLTAccResourceID		= @ResourceId +5
Set		@LocProfileResourceID	= @ResourceId +6
Set		@AccProfileResourceID	= @ResourceId +7

Set		@FromLocXSDFileID	= @FileId
Set		@ToLocXSDFileID		= @FileId +1
Set		@XSLTLocFileID		= @FileId +2
Set		@FromAccXSDFileID	= @FileId +3
Set		@ToAccXSDFileID		= @FileId +4
Set		@XSLTAccFileID		= @FileId +5

Set		@FromLocXSDFileResourceID	= @FileResourceId
Set		@ToLocXSDFileResourceID		= @FileResourceId +1
Set		@XSLTLocFileResourceID		= @FileResourceId +2
Set		@FromAccXSDFileResourceID	= @FileResourceId +3
Set		@ToAccXSDFileResourceID		= @FileResourceId +4
Set		@XSLTAccFileResourceID		= @FileResourceId +5

Set		@LocProfileId	= @ProfileId
Set		@AccProfileId	= @ProfileId +1

Set		@LocPofileResourceID	= @ProfileResourceId
Set		@AccPofileResourceID	= @ProfileResourceId +1



--Transform
Insert Into Transform Values (@TransformId,'Source Exposure Transform MEEQ','Source AccLoc to Canonical for EDM',1)

--Resource
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@FromLocXSDResourceID,	'Transform',@TransformId,NULL,120)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@ToLocXSDResourceID,		'Transform',@TransformId,NULL,121)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@XSLTLocResourceID,		'Transform',@TransformId,NULL,124)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@FromAccXSDResourceID,	'Transform',@TransformId,NULL,122)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@ToAccXSDResourceID,		'Transform',@TransformId,NULL,123)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@XSLTAccResourceID,		'Transform',@TransformId,NULL,125)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@LocProfileResourceID,	'Transform',@TransformId,NULL,118)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@AccProfileResourceID,	'Transform',@TransformId,NULL,119)

--File
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@FromLocXSDFileID,  N'Catrisks_SourceLoc.xsd', N'Source Loc Validation File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109)
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@ToLocXSDFileID,    N'Catrisks_CanLoc.xsd', N'Canonical Loc Validation File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109)
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@XSLTLocFileID,     N'MappingMapToCatrisks_CanLoc.xslt', N'Source to Canonical Loc Tranformation File', 1, 1, 105, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 110)
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@FromAccXSDFileID,  N'SourceAcc.xsd', N'Source Acc Validation File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109)
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@ToAccXSDFileID,    N'CanAcc.xsd', N'Canonical Loc Validation File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109)
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@XSLTAccFileID,     N'MappingMapToCanAcc.xslt', N'Source to Canonical Acc Tranformation File', 1, 1, 105, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 110)

--FileResource
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@FromLocXSDFileResourceID,	@FromLocXSDFileID,	@FromLocXSDResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@ToLocXSDFileResourceID,		@ToLocXSDFileID,	@ToLocXSDResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@XSLTLocFileResourceID,		@XSLTLocFileID,		@XSLTLocResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@FromAccXSDFileID,			@FromAccXSDFileID,	@FromAccXSDResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@ToAccXSDFileID,				@ToAccXSDFileID,	@ToAccXSDResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@XSLTAccFileResourceID,		@XSLTAccFileID,		@XSLTAccResourceID)

--Profile
INSERT [dbo].[Profile] ([ProfileID], [ProfileName], [ProfileTypeID]) VALUES (@LocProfileId, 'EDM Canonical Loc MEEQ', 1)
INSERT [dbo].[Profile] ([ProfileID], [ProfileName], [ProfileTypeID]) VALUES (@AccProfileId, 'EDM Canonical Acc MEEQ', 2)

--ProfileResource
INSERT [dbo].[ProfileResource] ([ProfileResourceID], [ProfileID], [ResourceId]) VALUES (@LocPofileResourceID, @LocProfileId, @LocProfileResourceID)
INSERT [dbo].[ProfileResource] ([ProfileResourceID], [ProfileID], [ResourceId]) VALUES (@AccPofileResourceID, @AccProfileId, @AccProfileResourceID)

--ProfileElements
insert into [ProfileElement] values (1+@ProfileElementId,'LocId',@LocProfileId,5,3)
insert into [ProfileElement] values (2+@ProfileElementId,'ACCNTNUM',@LocProfileId,16,6)
insert into [ProfileElement] values (3+@ProfileElementId,'LOCNUM',@LocProfileId,5,10)
insert into [ProfileElement] values (4+@ProfileElementId,'LATITUDE',@LocProfileId,5,8)
insert into [ProfileElement] values (5+@ProfileElementId,'LONGITUDE',@LocProfileId,5,9)
insert into [ProfileElement] values (6+@ProfileElementId,'POSTCODE',@LocProfileId,5,7)
insert into [ProfileElement] values (7+@ProfileElementId,'ADDRMATCH',@LocProfileId,5,48)
insert into [ProfileElement] values (8+@ProfileElementId,'STATE',@LocProfileId,5,51)    ------
insert into [ProfileElement] values (9+@ProfileElementId,'STATECODE',@LocProfileId,5,29)
insert into [ProfileElement] values (10+@ProfileElementId,'COUNTY',@LocProfileId,5,50)
insert into [ProfileElement] values (11+@ProfileElementId,'COUNTYCODE',@LocProfileId,5,30)
insert into [ProfileElement] values (12+@ProfileElementId,'CITY',@LocProfileId,5,11) ---------
insert into [ProfileElement] values (13+@ProfileElementId,'CITYCODE',@LocProfileId,5,12) ----------
insert into [ProfileElement] values (14+@ProfileElementId,'COUNTRY',@LocProfileId,5,52)
insert into [ProfileElement] values (15+@ProfileElementId,'CNTRYSCHEME',@LocProfileId,5,45)
insert into [ProfileElement] values (16+@ProfileElementId,'CNTRYCODE',@LocProfileId,5,46)
insert into [ProfileElement] values (17+@ProfileElementId,'BLDGSCHEME',@LocProfileId,5,11)
insert into [ProfileElement] values (18+@ProfileElementId,'BLDGCLASS',@LocProfileId,5,12)
insert into [ProfileElement] values (19+@ProfileElementId,'OCCSCHEME',@LocProfileId,5,13)
insert into [ProfileElement] values (20+@ProfileElementId,'OCCTYPE',@LocProfileId,5,14)
insert into [ProfileElement] values (21+@ProfileElementId,'NUMBLDGS',@LocProfileId,5,34)
insert into [ProfileElement] values (22+@ProfileElementId,'EQCV1VAL',@LocProfileId,5,2)
insert into [ProfileElement] values (23+@ProfileElementId,'EQCV1VCUR',@LocProfileId,5,47)
insert into [ProfileElement] values (24+@ProfileElementId,'EQCV1DED',@LocProfileId,14,16)
insert into [ProfileElement] values (25+@ProfileElementId,'EQCV1DCUR',@LocProfileId,14,47)
insert into [ProfileElement] values (26+@ProfileElementId,'EQCV1LIMIT',@LocProfileId,14,15)
insert into [ProfileElement] values (27+@ProfileElementId,'EQCV1LCUR',@LocProfileId,14,47)
insert into [ProfileElement] values (28+@ProfileElementId,'EQCV2VAL',@LocProfileId,5,2)
insert into [ProfileElement] values (29+@ProfileElementId,'EQCV2VCUR',@LocProfileId,5,47)
insert into [ProfileElement] values (30+@ProfileElementId,'EQCV2DED',@LocProfileId,14,16)
insert into [ProfileElement] values (31+@ProfileElementId,'EQCV2DCUR',@LocProfileId,14,47)
insert into [ProfileElement] values (32+@ProfileElementId,'EQCV2LIMIT',@LocProfileId,14,15)
insert into [ProfileElement] values (33+@ProfileElementId,'EQCV2LCUR',@LocProfileId,14,47)
insert into [ProfileElement] values (34+@ProfileElementId,'EQSITELIM',@LocProfileId,14,17)
insert into [ProfileElement] values (35+@ProfileElementId,'EQSITELCUR',@LocProfileId,14,47)
insert into [ProfileElement] values (36+@ProfileElementId,'EQSITEDED',@LocProfileId,14,18)
insert into [ProfileElement] values (37+@ProfileElementId,'EQSITEDCUR',@LocProfileId,14,47)
insert into [ProfileElement] values (38+@ProfileElementId,'EQCOMBINEDLIM',@LocProfileId,14,19)
insert into [ProfileElement] values (39+@ProfileElementId,'EQCOMBINEDLCUR',@LocProfileId,14,47)
insert into [ProfileElement] values (40+@ProfileElementId,'EQCOMBINEDDED',@LocProfileId,14,20)
insert into [ProfileElement] values (41+@ProfileElementId,'EQCOMBINEDDCUR',@LocProfileId,14,47)

insert into [ProfileElement] values (42+@ProfileElementId,'ROWID',@AccProfileId,16,1)
insert into [ProfileElement] values (43+@ProfileElementId,'ACCNTNUM',@AccProfileId,16,6)
insert into [ProfileElement] values (44+@ProfileElementId,'POLICYNUM',@AccProfileId,16,21)
insert into [ProfileElement] values (45+@ProfileElementId,'POLICYTYPE',@AccProfileId,16,22)
insert into [ProfileElement] values (46+@ProfileElementId,'UNDCOVAMT',@AccProfileId,20,23)
insert into [ProfileElement] values (47+@ProfileElementId,'PARTOF',@AccProfileId,20,24)
insert into [ProfileElement] values (48+@ProfileElementId,'MINDEDAMT',@AccProfileId,20,25)
insert into [ProfileElement] values (49+@ProfileElementId,'MAXDEDAMT',@AccProfileId,20,26)
insert into [ProfileElement] values (50+@ProfileElementId,'BLANDEDAMT',@AccProfileId,20,27)
insert into [ProfileElement] values (51+@ProfileElementId,'BLANLIMAMT',@AccProfileId,20,28)

--ProfileValueDetail
INSERT [dbo].[ProfileValueDetail] ([ProfileValueDetailID], [ProfileElementID],[PerilID],[CoverageTypeID],[ElementDimensionID]) VALUES (1+@ProfileValueDetailID ,22+@ProfileElementId,3,1,1)
INSERT [dbo].[ProfileValueDetail] ([ProfileValueDetailID], [ProfileElementID],[PerilID],[CoverageTypeID],[ElementDimensionID]) VALUES (2+@ProfileValueDetailID ,24+@ProfileElementId,3,1,1)
INSERT [dbo].[ProfileValueDetail] ([ProfileValueDetailID], [ProfileElementID],[PerilID],[CoverageTypeID],[ElementDimensionID]) VALUES (3+@ProfileValueDetailID ,26+@ProfileElementId,3,1,1)
INSERT [dbo].[ProfileValueDetail] ([ProfileValueDetailID], [ProfileElementID],[PerilID],[CoverageTypeID],[ElementDimensionID]) VALUES (4+@ProfileValueDetailID ,28+@ProfileElementId,3,3,2)
INSERT [dbo].[ProfileValueDetail] ([ProfileValueDetailID], [ProfileElementID],[PerilID],[CoverageTypeID],[ElementDimensionID]) VALUES (5+@ProfileValueDetailID ,30+@ProfileElementId,3,3,2)
INSERT [dbo].[ProfileValueDetail] ([ProfileValueDetailID], [ProfileElementID],[PerilID],[CoverageTypeID],[ElementDimensionID]) VALUES (6+@ProfileValueDetailID ,32+@ProfileElementId,3,3,2)

-------------canonical to model------------------------

Set	@ResourceId = (Select ISNULL(Max(ResourceId),0) + 1 From [Resource])
Set	@FileId = (Select ISNULL(Max(FileId),0) + 1 From [File])
Set	@FileResourceId = (Select ISNULL(Max(FileId),0) + 1 From [FileResource])
Set	@TransformId = (Select ISNULL(Max(TransformId),0) + 1 From [Transform])

Set		@FromLocXSDResourceID	= @ResourceId
Set		@ToLocXSDResourceID		= @ResourceId +1
Set		@XSLTLocResourceID		= @ResourceId +2

Set		@FromLocXSDFileID	= @FileId
Set		@ToLocXSDFileID		= @FileId +1
Set		@XSLTLocFileID		= @FileId +2

Set		@FromLocXSDFileResourceID	= @FileResourceId
Set		@ToLocXSDFileResourceID		= @FileResourceId +1
Set		@XSLTLocFileResourceID		= @FileResourceId +2


--Transform
Insert Into Transform Values (@TransformId,'Model Transform','Canonical to Model for Catrisks MEEQ',2)

--Resource
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@FromLocXSDResourceID,	'Transform',@TransformId,NULL,120)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@ToLocXSDResourceID,		'Transform',@TransformId,NULL,121)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@XSLTLocResourceID,		'Transform',@TransformId,NULL,124)

--File
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@FromLocXSDFileID,  N'Catrisks_CanLoc.xsd', N'Source Loc Validation File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109)
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@ToLocXSDFileID,    N'Catrisks_ModelLoc.xsd', N'Canonical Loc Validation File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109)
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@XSLTLocFileID,     N'MappingMapToCatrisks_ModelLoc.xslt', N'Source to Canonical Loc Tranformation File', 1, 1, 105, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 110)

--FileResource
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@FromLocXSDFileResourceID, @FromLocXSDFileID, @FromLocXSDResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@ToLocXSDFileResourceID, @ToLocXSDFileID, @ToLocXSDResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@XSLTLocFileResourceID, @XSLTLocFileID, @XSLTLocResourceID)



GO
