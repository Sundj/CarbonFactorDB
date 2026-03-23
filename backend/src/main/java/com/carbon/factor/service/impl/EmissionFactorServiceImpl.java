package com.carbon.factor.service.impl;

import com.carbon.factor.entity.EmissionFactor;
import com.carbon.factor.repository.EmissionFactorRepository;
import com.carbon.factor.service.EmissionFactorService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class EmissionFactorServiceImpl implements EmissionFactorService {
    
    @Autowired
    private EmissionFactorRepository emissionFactorRepository;
    
    @Override
    public Page<EmissionFactor> searchFactors(String keyword, Long category1Id, String scopeType, String region, Pageable pageable) {
        return emissionFactorRepository.searchFactors(keyword, category1Id, scopeType, region, pageable);
    }
    
    @Override
    public Optional<EmissionFactor> findByFactorCode(String factorCode) {
        return emissionFactorRepository.findByFactorCodeAndDeleted(factorCode, 0);
    }
    
    @Override
    public EmissionFactor saveFactor(EmissionFactor factor) {
        return emissionFactorRepository.save(factor);
    }
    
    @Override
    public void deleteFactor(Long id) {
        emissionFactorRepository.findById(id).ifPresent(factor -> {
            factor.setDeleted(1);
            emissionFactorRepository.save(factor);
        });
    }
    
    @Override
    public List<EmissionFactor> findLatestFactors() {
        return emissionFactorRepository.findLatestFactors();
    }
    
    @Override
    public List<EmissionFactor> findByCategory(Long category1Id) {
        return emissionFactorRepository.findByCategory1IdAndDeleted(category1Id, 0);
    }
    
    @Override
    public List<EmissionFactor> findByScopeType(String scopeType) {
        return emissionFactorRepository.findByScopeTypeAndDeleted(scopeType, 0);
    }
}
