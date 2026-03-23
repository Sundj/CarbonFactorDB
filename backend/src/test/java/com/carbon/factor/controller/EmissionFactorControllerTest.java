package com.carbon.factor.controller;

import com.carbon.factor.entity.EmissionFactor;
import com.carbon.factor.service.EmissionFactorService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * EmissionFactorController 单元测试
 */
@WebMvcTest(EmissionFactorController.class)
class EmissionFactorControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private EmissionFactorService emissionFactorService;

    @Autowired
    private ObjectMapper objectMapper;

    private EmissionFactor createTestFactor() {
        EmissionFactor factor = new EmissionFactor();
        factor.setId(1L);
        factor.setFactorCode("EF-COAL-001");
        factor.setFactorName("原煤");
        factor.setFactorValue(new BigDecimal("1.9003"));
        factor.setFactorUnit("tCO2e/t");
        factor.setScopeType("SCOPE1");
        factor.setApplicableRegion("全国");
        factor.setDataSource("国家清单指南");
        factor.setSourceYear(2023);
        factor.setDataQuality("高");
        return factor;
    }

    @Test
    @DisplayName("测试查询因子列表")
    void testSearchFactors() throws Exception {
        EmissionFactor factor = createTestFactor();
        Page<EmissionFactor> page = new PageImpl<>(
                Arrays.asList(factor), PageRequest.of(0, 10), 1);

        when(emissionFactorService.searchFactors(isNull(), isNull(), isNull(), isNull(), any()))
                .thenReturn(page);

        mockMvc.perform(get("/api/factors")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content[0].factorCode").value("EF-COAL-001"))
                .andExpect(jsonPath("$.content[0].factorName").value("原煤"));
    }

    @Test
    @DisplayName("测试根据编码查询因子")
    void testGetFactorByCode() throws Exception {
        EmissionFactor factor = createTestFactor();

        when(emissionFactorService.findByFactorCode("EF-COAL-001"))
                .thenReturn(Optional.of(factor));

        mockMvc.perform(get("/api/factors/EF-COAL-001")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.factorCode").value("EF-COAL-001"))
                .andExpect(jsonPath("$.factorName").value("原煤"));
    }

    @Test
    @DisplayName("测试查询不存在的因子")
    void testGetFactorNotFound() throws Exception {
        when(emissionFactorService.findByFactorCode("NOT-EXIST"))
                .thenReturn(Optional.empty());

        mockMvc.perform(get("/api/factors/NOT-EXIST")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("测试创建因子")
    void testCreateFactor() throws Exception {
        EmissionFactor factor = createTestFactor();

        when(emissionFactorService.saveFactor(any(EmissionFactor.class)))
                .thenReturn(factor);

        mockMvc.perform(post("/api/factors")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(factor)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.factorCode").value("EF-COAL-001"));
    }

    @Test
    @DisplayName("测试获取统计数据")
    void testGetStatistics() throws Exception {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalFactors", 3025);
        stats.put("scope1Count", 1500);
        stats.put("scope2Count", 1000);
        stats.put("scope3Count", 525);

        when(emissionFactorService.findLatestFactors()).thenReturn(Arrays.asList());
        when(emissionFactorService.findByScopeType("SCOPE1")).thenReturn(Arrays.asList());
        when(emissionFactorService.findByScopeType("SCOPE2")).thenReturn(Arrays.asList());
        when(emissionFactorService.findByScopeType("SCOPE3")).thenReturn(Arrays.asList());

        mockMvc.perform(get("/api/factors/statistics")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("测试按范围查询因子")
    void testGetFactorsByScope() throws Exception {
        EmissionFactor factor = createTestFactor();

        when(emissionFactorService.findByScopeType("SCOPE1"))
                .thenReturn(Arrays.asList(factor));

        mockMvc.perform(get("/api/factors/by-scope/SCOPE1")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].scopeType").value("SCOPE1"));
    }
}
