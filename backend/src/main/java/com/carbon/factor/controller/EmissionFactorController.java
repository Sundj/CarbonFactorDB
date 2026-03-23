package com.carbon.factor.controller;

import com.carbon.factor.entity.EmissionFactor;
import com.carbon.factor.service.EmissionFactorService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/factors")
@CrossOrigin(origins = "*")
public class EmissionFactorController {
    
    @Autowired
    private EmissionFactorService emissionFactorService;
    
    @GetMapping
    public ResponseEntity<Page<EmissionFactor>> searchFactors(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Long category1Id,
            @RequestParam(required = false) String scopeType,
            @RequestParam(required = false) String region,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Page<EmissionFactor> result = emissionFactorService.searchFactors(keyword, category1Id, scopeType, region, pageable);
        return ResponseEntity.ok(result);
    }
    
    @GetMapping("/{factorCode}")
    public ResponseEntity<EmissionFactor> getFactorByCode(@PathVariable String factorCode) {
        return emissionFactorService.findByFactorCode(factorCode)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    
    @GetMapping("/latest")
    public ResponseEntity<List<EmissionFactor>> getLatestFactors() {
        return ResponseEntity.ok(emissionFactorService.findLatestFactors());
    }
    
    @GetMapping("/by-category/{category1Id}")
    public ResponseEntity<List<EmissionFactor>> getFactorsByCategory(@PathVariable Long category1Id) {
        return ResponseEntity.ok(emissionFactorService.findByCategory(category1Id));
    }
    
    @GetMapping("/by-scope/{scopeType}")
    public ResponseEntity<List<EmissionFactor>> getFactorsByScope(@PathVariable String scopeType) {
        return ResponseEntity.ok(emissionFactorService.findByScopeType(scopeType));
    }
    
    @PostMapping
    public ResponseEntity<EmissionFactor> createFactor(@RequestBody EmissionFactor factor) {
        return ResponseEntity.ok(emissionFactorService.saveFactor(factor));
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<EmissionFactor> updateFactor(@PathVariable Long id, @RequestBody EmissionFactor factor) {
        factor.setId(id);
        return ResponseEntity.ok(emissionFactorService.saveFactor(factor));
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteFactor(@PathVariable Long id) {
        emissionFactorService.deleteFactor(id);
        return ResponseEntity.ok().build();
    }
    
    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getStatistics() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalFactors", emissionFactorService.findLatestFactors().size());
        stats.put("scope1Count", emissionFactorService.findByScopeType("SCOPE1").size());
        stats.put("scope2Count", emissionFactorService.findByScopeType("SCOPE2").size());
        stats.put("scope3Count", emissionFactorService.findByScopeType("SCOPE3").size());
        return ResponseEntity.ok(stats);
    }
}
