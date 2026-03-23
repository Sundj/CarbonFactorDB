package com.carbon.factor.repository;

import com.carbon.factor.entity.EmissionFactor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface EmissionFactorRepository extends JpaRepository<EmissionFactor, Long>, JpaSpecificationExecutor<EmissionFactor> {
    
    Optional<EmissionFactor> findByFactorCodeAndDeleted(String factorCode, Integer deleted);
    
    List<EmissionFactor> findByCategory1IdAndDeleted(Long category1Id, Integer deleted);
    
    List<EmissionFactor> findByScopeTypeAndDeleted(String scopeType, Integer deleted);
    
    @Query("SELECT ef FROM EmissionFactor ef WHERE ef.deleted = 0 AND " +
           "(:keyword IS NULL OR ef.factorName LIKE %:keyword% OR ef.factorCode LIKE %:keyword%) AND " +
           "(:category1Id IS NULL OR ef.category1Id = :category1Id) AND " +
           "(:scopeType IS NULL OR ef.scopeType = :scopeType) AND " +
           "(:region IS NULL OR ef.applicableRegion = :region)")
    Page<EmissionFactor> searchFactors(@Param("keyword") String keyword,
                                       @Param("category1Id") Long category1Id,
                                       @Param("scopeType") String scopeType,
                                       @Param("region") String region,
                                       Pageable pageable);
    
    @Query("SELECT ef FROM EmissionFactor ef WHERE ef.deleted = 0 AND ef.isLatestVersion = 1 " +
           "ORDER BY ef.sourceYear DESC")
    List<EmissionFactor> findLatestFactors();
}
