package com.carbon.factor.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 排放因子实体类
 * 对应国家温室气体排放因子数据库（第二版）数据结构
 */
@Entity
@Table(name = "emission_factor")
public class EmissionFactor {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "factor_code", nullable = false, unique = true, length = 50)
    private String factorCode;
    
    @Column(name = "factor_name", nullable = false, length = 200)
    private String factorName;
    
    @Column(name = "factor_alias", length = 200)
    private String factorAlias;
    
    // 分类关联
    @Column(name = "category1_id", nullable = false)
    private Long category1Id;
    
    @Column(name = "category2_id")
    private Long category2Id;
    
    @Column(name = "category3_id")
    private Long category3Id;
    
    // IPCC分类
    @Column(name = "ipcc_sector_code", length = 20)
    private String ipccSectorCode;
    
    @Column(name = "ipcc_sector_name", length = 100)
    private String ipccSectorName;
    
    @Column(name = "ipcc_category_code", length = 20)
    private String ipccCategoryCode;
    
    @Column(name = "ipcc_category_name", length = 100)
    private String ipccCategoryName;
    
    // 排放范围
    @Column(name = "scope_type", nullable = false, length = 20)
    private String scopeType;
    
    @Column(name = "scope_subcategory", length = 50)
    private String scopeSubcategory;
    
    // 因子数值
    @Column(name = "factor_value", nullable = false, precision = 20, scale = 10)
    private BigDecimal factorValue;
    
    @Column(name = "factor_unit", nullable = false, length = 50)
    private String factorUnit;
    
    @Column(name = "factor_unit_cn", length = 50)
    private String factorUnitCn;
    
    // 气体成分
    @Column(name = "co2_factor", precision = 20, scale = 10)
    private BigDecimal co2Factor;
    
    @Column(name = "ch4_factor", precision = 20, scale = 10)
    private BigDecimal ch4Factor;
    
    @Column(name = "n2o_factor", precision = 20, scale = 10)
    private BigDecimal n2oFactor;
    
    @Column(name = "other_ghg_factor", precision = 20, scale = 10)
    private BigDecimal otherGhgFactor;
    
    @Column(name = "gwp_version", length = 20)
    private String gwpVersion;
    
    // 适用条件
    @Column(name = "applicable_region", length = 100)
    private String applicableRegion;
    
    @Column(name = "applicable_province", length = 50)
    private String applicableProvince;
    
    @Column(name = "applicable_city", length = 50)
    private String applicableCity;
    
    @Column(name = "applicable_industry", length = 100)
    private String applicableIndustry;
    
    @Column(name = "applicable_scenario", length = 200)
    private String applicableScenario;
    
    // 数据来源
    @Column(name = "data_source", length = 200)
    private String dataSource;
    
    @Column(name = "source_document", length = 500)
    private String sourceDocument;
    
    @Column(name = "source_version", length = 50)
    private String sourceVersion;
    
    @Column(name = "source_year")
    private Integer sourceYear;
    
    // 数据质量
    @Column(name = "data_quality", length = 20)
    private String dataQuality;
    
    @Column(name = "confidence_level", length = 20)
    private String confidenceLevel;
    
    @Column(name = "uncertainty_range", length = 100)
    private String uncertaintyRange;
    
    // 计算说明
    @Column(name = "calculation_method", columnDefinition = "TEXT")
    private String calculationMethod;
    
    @Column(name = "calculation_boundary", columnDefinition = "TEXT")
    private String calculationBoundary;
    
    @Column(name = "technical_route", columnDefinition = "TEXT")
    private String technicalRoute;
    
    // 元数据
    @Column(name = "factor_version", nullable = false)
    private Integer factorVersion = 1;
    
    @Column(name = "is_latest_version", nullable = false)
    private Integer isLatestVersion = 1;
    
    @Column(name = "is_official", nullable = false)
    private Integer isOfficial = 1;
    
    @Column(name = "status", nullable = false)
    private Integer status = 1;
    
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @Column(name = "created_by")
    private Long createdBy;
    
    @Column(name = "updated_by")
    private Long updatedBy;
    
    @Column(name = "deleted", nullable = false)
    private Integer deleted = 0;
    
    // 关联分类
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category1_id", insertable = false, updatable = false)
    private FactorCategoryLevel1 category1;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category2_id", insertable = false, updatable = false)
    private FactorCategoryLevel2 category2;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category3_id", insertable = false, updatable = false)
    private FactorCategoryLevel3 category3;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
    
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getFactorCode() { return factorCode; }
    public void setFactorCode(String factorCode) { this.factorCode = factorCode; }
    
    public String getFactorName() { return factorName; }
    public void setFactorName(String factorName) { this.factorName = factorName; }
    
    public String getFactorAlias() { return factorAlias; }
    public void setFactorAlias(String factorAlias) { this.factorAlias = factorAlias; }
    
    public Long getCategory1Id() { return category1Id; }
    public void setCategory1Id(Long category1Id) { this.category1Id = category1Id; }
    
    public Long getCategory2Id() { return category2Id; }
    public void setCategory2Id(Long category2Id) { this.category2Id = category2Id; }
    
    public Long getCategory3Id() { return category3Id; }
    public void setCategory3Id(Long category3Id) { this.category3Id = category3Id; }
    
    public String getScopeType() { return scopeType; }
    public void setScopeType(String scopeType) { this.scopeType = scopeType; }
    
    public BigDecimal getFactorValue() { return factorValue; }
    public void setFactorValue(BigDecimal factorValue) { this.factorValue = factorValue; }
    
    public String getFactorUnit() { return factorUnit; }
    public void setFactorUnit(String factorUnit) { this.factorUnit = factorUnit; }
    
    public String getApplicableRegion() { return applicableRegion; }
    public void setApplicableRegion(String applicableRegion) { this.applicableRegion = applicableRegion; }
    
    public String getDataSource() { return dataSource; }
    public void setDataSource(String dataSource) { this.dataSource = dataSource; }
    
    public Integer getSourceYear() { return sourceYear; }
    public void setSourceYear(Integer sourceYear) { this.sourceYear = sourceYear; }
    
    public String getDataQuality() { return dataQuality; }
    public void setDataQuality(String dataQuality) { this.dataQuality = dataQuality; }
    
    public FactorCategoryLevel1 getCategory1() { return category1; }
    public void setCategory1(FactorCategoryLevel1 category1) { this.category1 = category1; }
    
    public FactorCategoryLevel2 getCategory2() { return category2; }
    public void setCategory2(FactorCategoryLevel2 category2) { this.category2 = category2; }
    
    public FactorCategoryLevel3 getCategory3() { return category3; }
    public void setCategory3(FactorCategoryLevel3 category3) { this.category3 = category3; }
}
