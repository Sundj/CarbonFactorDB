package com.carbon.factor.service;

import com.carbon.factor.entity.EmissionFactor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.Optional;

public interface EmissionFactorService {
    
    Page<EmissionFactor> searchFactors(String keyword, Long category1Id, String scopeType, String region, Pageable pageable);
    
    Optional<EmissionFactor> findByFactorCode(String factorCode);
    
    EmissionFactor saveFactor(EmissionFactor factor);
    
    void deleteFactor(Long id);
    
    List<EmissionFactor> findLatestFactors();
    
    List<EmissionFactor> findByCategory(Long category1Id);
    
    List<EmissionFactor> findByScopeType(String scopeType);
}
