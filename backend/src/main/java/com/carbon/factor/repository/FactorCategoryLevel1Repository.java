package com.carbon.factor.repository;

import com.carbon.factor.entity.FactorCategoryLevel1;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface FactorCategoryLevel1Repository extends JpaRepository<FactorCategoryLevel1, Long> {
    List<FactorCategoryLevel1> findByStatusAndDeletedOrderBySortOrderAsc(Integer status, Integer deleted);
}
