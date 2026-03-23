package com.carbon.factor.service;

import com.carbon.factor.entity.EmissionFactor;
import com.carbon.factor.entity.FactorCategoryLevel1;
import com.carbon.factor.repository.EmissionFactorRepository;
import com.carbon.factor.repository.FactorCategoryLevel1Repository;
import com.carbon.factor.service.impl.EmissionFactorServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * EmissionFactorService 单元测试
 */
@ExtendWith(MockitoExtension.class)
class EmissionFactorServiceTest {

    @Mock
    private EmissionFactorRepository emissionFactorRepository;

    @Mock
    private FactorCategoryLevel1Repository categoryRepository;

    @InjectMocks
    private EmissionFactorServiceImpl emissionFactorService;

    private EmissionFactor testFactor;
    private FactorCategoryLevel1 testCategory;

    @BeforeEach
    void setUp() {
        // 设置测试分类
        testCategory = new FactorCategoryLevel1();
        testCategory.setId(1L);
        testCategory.setCategoryCode("ENERGY");
        testCategory.setCategoryName("能源活动");
        testCategory.setDescription("化石燃料燃烧等能源相关活动");
        testCategory.setSortOrder(1);

        // 设置测试排放因子
        testFactor = new EmissionFactor();
        testFactor.setId(1L);
        testFactor.setFactorCode("EF-COAL-001");
        testFactor.setFactorName("原煤");
        testFactor.setFactorValue(new BigDecimal("1.9003"));
        testFactor.setFactorUnit("tCO2e/t");
        testFactor.setScopeType("SCOPE1");
        testFactor.setScopeSubcategory("固定源燃烧");
        testFactor.setApplicableRegion("全国");
        testFactor.setDataSource("国家清单指南");
        testFactor.setSourceYear(2023);
        testFactor.setDataQuality("高");
        testFactor.setFactorVersion(1);
        testFactor.setIsLatestVersion(1);
        testFactor.setStatus(1);
        testFactor.setDeleted(0);
    }

    @Test
    @DisplayName("测试根据编码查询排放因子")
    void testFindByFactorCode() {
        when(emissionFactorRepository.findByFactorCodeAndDeleted("EF-COAL-001", 0))
                .thenReturn(Optional.of(testFactor));

        Optional<EmissionFactor> result = emissionFactorService.findByFactorCode("EF-COAL-001");

        assertTrue(result.isPresent());
        assertEquals("EF-COAL-001", result.get().getFactorCode());
        assertEquals("原煤", result.get().getFactorName());
        verify(emissionFactorRepository).findByFactorCodeAndDeleted("EF-COAL-001", 0);
    }

    @Test
    @DisplayName("测试分页搜索排放因子")
    void testSearchFactors() {
        List<EmissionFactor> factors = Arrays.asList(testFactor);
        Page<EmissionFactor> factorPage = new PageImpl<>(factors, PageRequest.of(0, 10), 1);

        when(emissionFactorRepository.searchFactors(
                eq("煤炭"), isNull(), isNull(), isNull(), any(Pageable.class)))
                .thenReturn(factorPage);

        Page<EmissionFactor> result = emissionFactorService.searchFactors(
                "煤炭", null, null, null, PageRequest.of(0, 10));

        assertNotNull(result);
        assertEquals(1, result.getTotalElements());
        assertEquals("原煤", result.getContent().get(0).getFactorName());
    }

    @Test
    @DisplayName("测试保存排放因子")
    void testSaveFactor() {
        when(emissionFactorRepository.save(any(EmissionFactor.class)))
                .thenReturn(testFactor);

        EmissionFactor result = emissionFactorService.saveFactor(testFactor);

        assertNotNull(result);
        assertEquals("EF-COAL-001", result.getFactorCode());
        verify(emissionFactorRepository).save(testFactor);
    }

    @Test
    @DisplayName("测试删除排放因子")
    void testDeleteFactor() {
        when(emissionFactorRepository.findById(1L))
                .thenReturn(Optional.of(testFactor));
        when(emissionFactorRepository.save(any(EmissionFactor.class)))
                .thenReturn(testFactor);

        emissionFactorService.deleteFactor(1L);

        verify(emissionFactorRepository).findById(1L);
        verify(emissionFactorRepository).save(argThat(factor -> factor.getDeleted() == 1));
    }

    @Test
    @DisplayName("测试查询最新版本因子")
    void testFindLatestFactors() {
        when(emissionFactorRepository.findLatestFactors())
                .thenReturn(Arrays.asList(testFactor));

        List<EmissionFactor> results = emissionFactorService.findLatestFactors();

        assertNotNull(results);
        assertEquals(1, results.size());
        assertEquals(1, results.get(0).getIsLatestVersion());
    }

    @Test
    @DisplayName("测试按分类查询因子")
    void testFindByCategory() {
        when(emissionFactorRepository.findByCategory1IdAndDeleted(1L, 0))
                .thenReturn(Arrays.asList(testFactor));

        List<EmissionFactor> results = emissionFactorService.findByCategory(1L);

        assertNotNull(results);
        assertEquals(1, results.size());
        verify(emissionFactorRepository).findByCategory1IdAndDeleted(1L, 0);
    }

    @Test
    @DisplayName("测试按排放范围查询因子")
    void testFindByScopeType() {
        when(emissionFactorRepository.findByScopeTypeAndDeleted("SCOPE1", 0))
                .thenReturn(Arrays.asList(testFactor));

        List<EmissionFactor> results = emissionFactorService.findByScopeType("SCOPE1");

        assertNotNull(results);
        assertEquals(1, results.size());
        assertEquals("SCOPE1", results.get(0).getScopeType());
    }

    @Test
    @DisplayName("测试因子值计算")
    void testFactorValueCalculation() {
        BigDecimal activityValue = new BigDecimal("1000.00");
        BigDecimal factorValue = testFactor.getFactorValue();

        BigDecimal emission = activityValue.multiply(factorValue);

        assertEquals(0, emission.compareTo(new BigDecimal("1900.30")));
    }
}
