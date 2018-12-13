
------------------------------------------
--Oasis PiWind
------------------------------------------
Declare	@SupplierId int = (Select ISNULL(Max(SupplierId),0) + 1 From Supplier)
Declare	@ModelFamilyId int = (Select ISNULL(Max(ModelFamilyId),0) + 1 From ModelFamily)
Declare	@ModelId int = (Select ISNULL(Max(ModelId),0) + 1 From Model)
Declare	@ServiceId int = (Select ISNULL(Max(ServiceId),0) + 1 From Service)
Declare	@OasisSystemId int = (Select ISNULL(Max(OasisSystemId),0) + 1 From OasisSystem)
Declare	@OasisSystemServiceId int = (Select ISNULL(Max(OasisSystemServiceId),0) + 1 From OasisSystemService)
Declare	@ModelResourceId int = (Select ISNULL(Max(ModelResourceId),0) From ModelResource)
Declare	@ModelPerilId int = (Select ISNULL(Max(ModelPerilId),0) From ModelPeril)
Declare	@ModelCoverageTypeId int = (Select ISNULL(Max(ModelCoverageTypeId),0) From ModelCoverageType)

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
		VALUES (@SupplierId,N'',N'OasisLMF',N'OasisLMF',N'',N'',N'',0)

--ModelFamily
INSERT [dbo].[ModelFamily] ([ModelFamilyID], [ModelFamilyName], [SupplierID]) 
		VALUES (@ModelFamilyId, N'Pi', @SupplierId)

--Model
INSERT [dbo].[Model] ([ModelID], [ModelName], [ModelFamilyID], [ModelDescription], [VersionRef], [ReleaseDate], [Contact], [ModelTypeId], [Deleted]) 
		VALUES (@ModelId, N'PiWind OED', @ModelFamilyId, N'PiWind', N'1.0', N'Dec 2018', N'Ben Hayes', 1, 0)

--Service
INSERT [dbo].[Service] ([ServiceID], [ServiceName], [ServiceDesc], [ServiceTypeId], [ModelId]) 
		VALUES (@ServiceId, N'OasisLMF PiWind Oasis', N'PiWind Oasis Mid Tier', 1, @ModelId)
INSERT [dbo].[Service] ([ServiceID], [ServiceName], [ServiceDesc], [ServiceTypeId], [ModelId]) 
		VALUES (@ServiceId+1, N'OasisLMF PiWind API', N'PiWind Oasis Key Lookup Service', 2, @ModelId)

--OasisSystem
INSERT [dbo].[OasisSystem] ([OasisSystemID], [OasisSystemName], [OasisSystemDescription], [url], [Port], [SysConfigID]) 
		VALUES (@OasisSystemId, N'PiWind Oasis Mid Tier', N'Piwind Oasis Mid Tier', N'%OASIS_API_IP%', %OASIS_API_PORT%, 4)
INSERT [dbo].[OasisSystem] ([OasisSystemID], [OasisSystemName], [OasisSystemDescription], [url], [Port], [SysConfigID]) 
		VALUES (@OasisSystemId+1, N'PiWind API', N'PiWind Keys Service', N'http://%PIWIND_KEYS_IP%:%PIWIND_KEYS_PORT%/OasisLMF/PiWind/0.0.0.1/get_keys', NULL, NULL)


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
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'PiWind API', 1000, @OasisSystemID+1, @ModelID, N'')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'ModelGroupField', 300, @OasisSystemID, @ModelID, N'AreaPerilID')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'module_supplier_id', 301, @OasisSystemID, @ModelID, N'OasisLMF')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'model_version_id', 302, @OasisSystemID, @ModelID, N'PiWind')
INSERT #ModelResource (ModelResourceName,ResourceTypeID,OasisSystemID,ModelID,ModelResourceValue) VALUES (N'peril_wind', 1001, @OasisSystemId, @ModelID, N'checkbox')
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
		VALUES (@ModelLicenseId, @ModelId, 1, N'Oasis Model License', N'Oasis Model License', '01/01/1900', '12/31/9999', 'Dummy License', 'BH')

--OasisUser
INSERT [dbo].[OasisUser] ([OasisUserID], [OasisUserName], [ModelLicenseID], [OasisSystemID], [SystemLogin], [SystemPassword], [Django Login], [Django Password]) 
		VALUES (@OasisUserId, N'OasisUserPiWind', @ModelLicenseId, @OasisSystemId, N'Root', N'Password', N'', N'')

--UserLicense
INSERT [dbo].[UserLicense] ([UserLicenseId], [BFEUserID], [OasisUserID]) VALUES (@UserLicenseId, 1, @OasisUserId)

--ModelPeril
INSERT ModelPeril Values (@ModelPerilId+1,@ModelId,1,'1','Wind')

--ModelPeril
INSERT ModelCoverageType Values (@ModelCoverageTypeId+1,@ModelId,1,'1','Buildings')

---------------------------------------------------------
--Transforms
---------------------------------------------------------
--Params
Set	@ResourceId = (Select ISNULL(Max(ResourceId),0) + 1 From [Resource])
Set	@FileId = (Select ISNULL(Max(FileId),0) + 1 From [File])
Set	@FileResourceId = (Select ISNULL(Max(FileResourceId),0) + 1 From [FileResource])
Set	@TransformId = (Select ISNULL(Max(TransformId),0) + 1 From [Transform])
Set	@ProfileId = (Select ISNULL(Max(ProfileId),0) + 1 From [Profile])

--Loc
--
-- |XSD1|-->|XSLT1|-->|XSD2a|
--                       |
--                       V
--                    |XSD2b|-->|XSLT2|-->|XSD3|
--                       |
--                       V
--                   |Profile1|
--Acc
--
-- |XSD4|-->|XSLT3|-->|XSD5a|
--                       |
--                       V
--                    |XSD5b|
--                       |
--                       V
--                   |Profile2|

--Declare Resource IDs
Declare @FromLocXSDResourceID		int = @ResourceId + 0  -- XSD1
Declare @XSLTLocResourceID			int = @ResourceId + 1  -- XSLT1
Declare @ToLocAXSDResourceID		int = @ResourceId + 2  -- XSD2a
Declare @ToLocBXSDResourceID		int = @ResourceId + 3  -- XSD2b
Declare @FromModelXSDResourceID		int = @ResourceId + 4  -- XSLT2
Declare @XSLTModelResourceID		int = @ResourceId + 5  -- XSLT2
Declare @ToModelXSDResourceID		int = @ResourceId + 6  -- XSD3
Declare @LocProfileResourceID		int = @ResourceId + 7  -- Profile1
Declare @FromAccXSDResourceID		int = @ResourceId + 8  -- XSD4
Declare @XSLTAccResourceID			int = @ResourceId + 9  -- XSLT3
Declare @ToAccAXSDResourceID		int = @ResourceId + 10 -- XSD5a
Declare @ToAccBXSDResourceID		int = @ResourceId + 11 -- XSD5b
Declare @AccProfileResourceID		int = @ResourceId + 12 -- Profile2

--Declare File IDs
Declare @FromLocXSDFileID			int = @FileId + 0  -- XSD1
Declare @XSLTLocFileID				int = @FileId + 1  -- XSLT1
Declare @ToLocAXSDFileID			int = @FileId + 2  -- XSD2a
Declare @ToLocBXSDFileID			int = @FileId + 3  -- XSD2b
Declare @XSLTModelFileID			int = @FileId + 4  -- XSLT2
Declare @ToModelXSDFileID			int = @FileId + 5  -- XSD3
Declare @FromAccXSDFileID			int = @FileId + 6  -- XSD4
Declare @XSLTAccFileID				int = @FileId + 7  -- XSLT3
Declare @ToAccAXSDFileID			int = @FileId + 8  -- XSD5a
Declare @ToAccBXSDFileID			int = @FileId + 9  -- XSD5b

--Declare File Resource IDs
Declare @FromLocXSDFileResourceID	int = @FileResourceId + 0  -- XSD1
Declare @XSLTLocFileResourceID		int = @FileResourceId + 1  -- XSLT1
Declare @ToLocAXSDFileResourceID	int = @FileResourceId + 2  -- XSD2a
Declare @ToLocBXSDFileResourceID	int = @FileResourceId + 3  -- XSD2b
Declare @FromModelXSDFileResourceID int = @FileResourceId + 4  -- XSD2b
Declare @XSLTModelFileResourceID	int = @FileResourceId + 5  -- XSLT2
Declare @ToModelXSDFileResourceID	int = @FileResourceId + 6  -- XSD3
Declare @FromAccXSDFileResourceID	int = @FileResourceId + 7  -- XSD4
Declare @XSLTAccFileResourceID		int = @FileResourceId + 8  -- XSLT3
Declare @ToAccAXSDFileResourceID	int = @FileResourceId + 9  -- XSD5a
Declare @ToAccBXSDFileResourceID	int = @FileResourceId + 10 -- XSD5b

--Declare Profile IDs
Declare @LocProfileId int = @ProfileID     -- Profile1
Declare @AccProfileId int = @ProfileID + 1 -- Profile2

-------------insert data------------------------
--Transform
Insert Into Transform Values (@TransformId,'OED Source to Canonical','Source OED to Canonical for EDM',1)
Insert Into Transform Values (@TransformId+1,'OED Canonical to PiWind Model','Canonical OED to Model for PiWind',2)
Insert Into ModelTransform Values (@ModelId,@TransformId)
Insert Into ModelTransform Values (@ModelId,@TransformId+1)

--Resource
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@FromLocXSDResourceID,	'Transform',@TransformId,NULL,120)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@XSLTLocResourceID,		'Transform',@TransformId,NULL,124)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@ToLocAXSDResourceID,		'Transform',@TransformId,NULL,121)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@ToLocBXSDResourceID,		'Transform',@TransformId,NULL,129)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@FromModelXSDResourceID,	'Transform',@TransformId+1,NULL,120)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@XSLTModelResourceID,		'Transform',@TransformId+1,NULL,124)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@ToModelXSDResourceID,	'Transform',@TransformId+1,NULL,121)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@LocProfileResourceID,	'Transform',@TransformId,NULL,118)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@FromAccXSDResourceID,	'Transform',@TransformId,NULL,122)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@XSLTAccResourceID,		'Transform',@TransformId,NULL,125)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@ToAccAXSDResourceID,		'Transform',@TransformId,NULL,123)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@ToAccBXSDResourceID,		'Transform',@TransformId,NULL,130)
INSERT [dbo].[Resource] ([ResourceId], [ResourceTable], [ResourceKey], [ResourceQualifier], [ResourceTypeID]) VALUES (@AccProfileResourceID,	'Transform',@TransformId,NULL,119)

--File
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@FromLocXSDFileID,		N'OED_SourceLoc.xsd', N'Source Loc Validation File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109) --XSD1
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@XSLTLocFileID,			N'MappingMapToOED_CanLocA.xslt', N'Source to Canonical Loc Tranformation File', 1, 1, 105, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 110) --XSLT1
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@ToLocAXSDFileID,		N'OED_CanLocA.xsd', N'Canonical Loc Validation A File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109) --XSD2a
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@ToLocBXSDFileID,		N'OED_CanLocB.xsd', N'Canonical Loc Validation B File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109) --XSD2b
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@XSLTModelFileID,		N'MappingMapOEDTopiwind_modelloc.xslt', N'Canonical to Model Loc Tranformation File', 1, 1, 105, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 110) --XSLT2
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@ToModelXSDFileID,		N'piwind_modelloc.xsd', N'Model Loc Validation File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109) --XSD3
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@FromAccXSDFileID,		N'OED_SourceAcc.xsd', N'Source Acc Validation File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109) --XSD4
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@XSLTAccFileID,			N'MappingMapToOED_CanAccA.xslt', N'Source to Canonical Acc Tranformation File', 1, 1, 105, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 110) --XSLT3
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@ToAccAXSDFileID,		N'OED_CanAcc_A.xsd', N'Canonical Acc Validation File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109) --XSD5a
INSERT [dbo].[File] ([FileId], [FileName], [FileDesc], [SourceID], [OwnerID], [LocationID], [DateTimeCreated], [DateTimeUpdated], [DateTimeDeleted], [OwnerNameCreated], [OwnerNameUpdated], [OwnerNameDeleted], [FileTypeId]) VALUES (@ToAccBXSDFileID,		N'OED_CanAcc_B.xsd', N'Canonical Acc Profile File', 1, 1, 106, getdate(), getdate(), NULL, N'Sys', N'Sys', NULL, 109) --XSD5b


--FileResource
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@FromLocXSDFileResourceID,	@FromLocXSDFileID,	@FromLocXSDResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@XSLTLocFileResourceID,		@XSLTLocFileID,		@XSLTLocResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@ToLocAXSDFileResourceID,	@ToLocAXSDFileID,	@ToLocAXSDResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@ToLocBXSDFileResourceID,	@ToLocBXSDFileID,	@ToLocBXSDResourceID)

INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@FromModelXSDFileResourceID,	@ToLocBXSDFileID,	@FromModelXSDResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@XSLTModelFileResourceID,	@XSLTModelFileID,	@XSLTModelResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@ToModelXSDFileResourceID,	@ToModelXSDFileID,	@ToModelXSDResourceID)

INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@FromAccXSDFileResourceID,	@FromAccXSDFileID,	@FromAccXSDResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@XSLTAccFileResourceID,		@XSLTAccFileID,		@XSLTAccResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@ToAccAXSDFileResourceID,	@ToAccAXSDFileID,	@ToAccAXSDResourceID)
INSERT [dbo].[FileResource] ([FileResourceId], [FileId], [ResourceId]) VALUES (@ToAccBXSDFileResourceID,	@ToAccBXSDFileID,	@ToAccBXSDResourceID)

--Profile
INSERT [dbo].[Profile] ([ProfileID], [ProfileName], [ProfileTypeID]) VALUES (@LocProfileId, 'OED Canonical Loc Catrisks MENAEQ', 1)
INSERT [dbo].[Profile] ([ProfileID], [ProfileName], [ProfileTypeID]) VALUES (@AccProfileId, 'OED Canonical Acc Catrisks MENAEQ', 2)

--ProfileResource
INSERT [dbo].[ProfileResource] ([ProfileResourceID], [ProfileID], [ResourceId]) VALUES (@ProfileResourceId, @LocProfileId, @LocProfileResourceID)
INSERT [dbo].[ProfileResource] ([ProfileResourceID], [ProfileID], [ResourceId]) VALUES (@ProfileResourceId+1, @AccProfileId, @AccProfileResourceID)


--ProfileElements
declare @int int = 0, @int2 int = 0
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ROW_ID',@LocProfileId,5,3) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PortNumber',@LocProfileId,5,62) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccNumber',@LocProfileId,16,6) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocNumber',@LocProfileId,5,10) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocName',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocGroup',@LocProfileId,5,63) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'IsPrimary',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'IsTenant',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BuildingID',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocInceptionDate',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocExpiryDate',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PercentComplete',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CompletionDate',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CountryCode',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Latitude',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Longitude',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'StreetAddress',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PostalCode',@LocProfileId,5,7) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'City',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AreaCode',@LocProfileId,5,29) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AreaName',@LocProfileId,5,0)
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GeogScheme1',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GeogName1',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GeogScheme2',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GeogName2',@LocProfileId,5,0)
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GeogScheme3',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GeogName3',@LocProfileId,5,0)
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GeogScheme4',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GeogName4',@LocProfileId,5,0)
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GeogScheme5',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GeogName5',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AddressMatch',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GeocodeQuality',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Geocoder',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'OrgOccupancyScheme',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'OrgOccupancyCode',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'OrgConstructionScheme',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'OrgConstructionCode',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'OccupancyCode',@LocProfileId,5,14) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ConstructionCode',@LocProfileId,5,12) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'YearBuilt',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'NumberOfStories',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'NumberOfBuildings',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'FloorArea',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'FloorAreaUnit',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocUserDef1',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocUserDef2',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocUserDef3',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocUserDef4',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocUserDef5',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocPerilsCovered',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BuildingTIV',@LocProfileId,5,2) set @int2=@int2+1INSERT [dbo].[ProfileValueDetail] ([ProfileValueDetailID], [ProfileElementID],[PerilID],[CoverageTypeID],[ElementDimensionID]) VALUES (@int2+@ProfileValueDetailID ,@int+@ProfileElementId,@ModelPerilId+1,@ModelCoverageTypeId+1,1)
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'OtherTIV',@LocProfileId,5,2)
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ContentsTIV',@LocProfileId,5,2) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BITIV',@LocProfileId,5,2) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BIPOI',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocCurrency',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocGrossPremium',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocTax',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocBrokerage',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocNetPremium',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'NonCatGroundUpLoss',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocParticipation',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PayoutBasis',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ReinsTag',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondNumber',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondPriority',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedCode1Building',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedType1Building',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDed1Building',@LocProfileId,14,16) set @int2=@int2+1INSERT [dbo].[ProfileValueDetail] ([ProfileValueDetailID], [ProfileElementID],[PerilID],[CoverageTypeID],[ElementDimensionID]) VALUES (@int2+@ProfileValueDetailID ,@int+@ProfileElementId,@ModelPerilId+1,@ModelCoverageTypeId+1,1)
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMinDed1Building',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMaxDed1Building',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedCode2Other',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedType2Other',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDed2Other',@LocProfileId,14,16) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMinDed2Other',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMaxDed2Other',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedCode3Contents',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedType3Contents',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDed3Contents',@LocProfileId,14,16) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMinDed3Contents',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMaxDed3Contents',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedCode4BI',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedType4BI',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDed4BI',@LocProfileId,14,16) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMinDed4BI',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMaxDed4BI',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedCode5PD',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedType5PD',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDed5PD',@LocProfileId,14,20) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMinDed5PD',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMaxDed5PD',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedCode6All',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDedType6All',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocDed6All',@LocProfileId,14,18) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMinDed6All',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocMaxDed6All',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimitCode1Building',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimitType1Building',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimit1Building',@LocProfileId,14,15) set @int2=@int2+1INSERT [dbo].[ProfileValueDetail] ([ProfileValueDetailID], [ProfileElementID],[PerilID],[CoverageTypeID],[ElementDimensionID]) VALUES (@int2+@ProfileValueDetailID ,@int+@ProfileElementId,@ModelPerilId+1,@ModelCoverageTypeId+1,1)
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimitCode2Other',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimitType2Other',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimit2Other',@LocProfileId,14,15) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimitCode3Contents',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimitType3Contents',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimit3Contents',@LocProfileId,14,15) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimitType4BI',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimit4BI',@LocProfileId,14,15) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimitCode5PD',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimitType5PD',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimit5PD',@LocProfileId,14,19) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimitCode6All',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimitType6All',@LocProfileId,14,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocLimit6All',@LocProfileId,14,17) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BIWaitingPeriod',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LocPeril',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'YearUpgraded',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'SurgeLeakage',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'SprinklerType',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofCover',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofYearBuilt',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofGeometry',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofEquipment',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofFrame',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofMaintenance',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BuildingCondition',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofAttachedStructure',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofDeck',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofPitch',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofAnchorage',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofDeckAttachment',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'RoofCoverAttachment',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GlassType',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LatticeType',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'FloodZone',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'SoftStory',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Basement',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BasementLevelCount',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'WindowProtection',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'FoundationType',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'WallAttachedStructure',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AppurtenantStructure',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ConstructionQuality',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GroundEquipment',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'EquipmentBracing',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Flashing',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BuildingShape',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ShapeIrregularity',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Pounding',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Ornamentation',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'SpecialEQConstruction',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Retrofit',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CrippleWalls',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'FoundationConnection',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ShortColumn',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Fatigue',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Cladding',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BIPreparedness',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BIRedundancy',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BuildingElevation',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BuildingElevationUnit',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Datum',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GroundElevation',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'GroundElevationUnit',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Tank',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Redundancy',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'InternalPartition',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ExternalDoors',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Torsion',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'MechanicalEquipmentSide',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ContentsWindVuln',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ContentsFloodVuln',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ContentsQuakeVuln',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'SmallDebris',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'FloorsOccupied',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'FloodDefenseElevation',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'FloodDefenseElevationUnit',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'FloodDebrisResilience',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BaseFloodElevation',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BaseFloodElevationUnit',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BuildingHeight',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BuildingHeightUnit',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BuildingValuation',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'TreeExposure',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Chimney',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BuildingType',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Packaging',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Protection',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'SalvageProtection',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ValuablesStorage',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'DaysHeld',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BrickVeneer',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'FEMACompliance',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CustomFloodSOP',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CustomFloodZone',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'MultiStoryHall',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BuildingExteriorOpening',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ServiceEquipmentProtection',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'TallOneStory',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'TerrainRoughness',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'NumberOfEmployees',@LocProfileId,5,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Payroll',@LocProfileId,5,0)

set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ROW_ID',@AccProfileId,16,1) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PortNumber',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PortName',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PortNotes',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccNumber',@AccProfileId,16,6) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccName',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccGroup',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccStatus',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ExpiringAccNumber',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CedantName',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccCurrency',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccUserDef1',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccUserDef2',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccUserDef3',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccUserDef4',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccUserDef5',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccPeril',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedCode1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedType1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDed1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMinDed1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMaxDed1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedCode2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedType2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDed2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMinDed2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMaxDed2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedCode3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedType3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDed3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMinDed3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMaxDed3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedCode4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedType4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDed4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMinDed4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMaxDed4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedCode5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedType5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDed5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMinDed5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMaxDed5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedCode6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDedType6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccDed6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMinDed6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccMaxDed6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitCode1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitType1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimit1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitCode2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitType2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimit2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitCode3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitType3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimit3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitCode4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitType4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimit4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitCode5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitType5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimit5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitCode6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimitType6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'AccLimit6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolNumber',@AccProfileId,16,21) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolStatus',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolInceptionDate',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolExpiryDate',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ProducerName',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'Underwriter',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'BranchName',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LOB',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ExpiringPolNumber',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolPerilsCovered',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolGrossPremium',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolTax',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolBrokerage',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolNetPremium',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LayerNumber',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LayerParticipation',@AccProfileId,16,57) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LayerLimit',@AccProfileId,16,24) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'LayerAttachment',@AccProfileId,16,23) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'HoursClause',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolPeril',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedCode1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedType1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDed1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMinDed1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMaxDed1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedCode2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedType2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDed2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMinDed2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMaxDed2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedCode3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedType3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDed3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMinDed3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMaxDed3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedCode4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedType4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDed4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMinDed4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMaxDed4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedCode5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedType5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDed5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMinDed5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMaxDed5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedCode6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDedType6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolDed6All',@AccProfileId,20,27) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMinDed6All',@AccProfileId,20,25) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolMaxDed6All',@AccProfileId,20,26) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitCode1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitType1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimit1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitCode2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitType2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimit2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitCode3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitType3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimit3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitCode4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitType4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimit4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitCode5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitType5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimit5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitCode6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimitType6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolLimit6All',@AccProfileId,20,24) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'StepFunctionName',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'StepTriggerType',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'StepNumber',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'StartTriggerBuilding',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'EndTriggerBuilding',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'DeductibleBuilding',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PayOutBuilding',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'StartTriggerContent',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'EndTriggerContent',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'DeductibleContent',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PayOutContent',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'StartTriggerBuildingContent',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'EndTriggerBuildingContent',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'DeductibleBuildingContent',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PayOutBuildingContent',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'MinimumTIV',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'ScaleFactor',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'IsLimitAtDamage',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolUserDef1',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolUserDef2',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolUserDef3',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolUserDef4',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'PolUserDef5',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondNumber',@AccProfileId,16,54) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondName',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondPeril',@AccProfileId,16,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedCode1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedType1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDed1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMinDed1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMaxDed1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedCode2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedType2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDed2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMinDed2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMaxDed2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedCode3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedType3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDed3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMinDed3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMaxDed3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedCode4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedType4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDed4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMinDed4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMaxDed4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedCode5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedType5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDed5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMinDed5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMaxDed5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedCode6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDedType6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondDed6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMinDed6All',@AccProfileId,20,56) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondMaxDed6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitCode1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitType1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimit1Building',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitCode2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitType2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimit2Other',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitCode3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitType3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimit3Contents',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitCode4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitType4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimit4BI',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitCode5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitType5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimit5PD',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitCode6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimitType6All',@AccProfileId,20,0) 
set @int=@int+1  insert into [ProfileElement] values (@int+@ProfileElementId,'CondLimit6All',@AccProfileId,20,55) 


GO
