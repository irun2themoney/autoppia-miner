"""
Tests for Autoppia Worker
"""

import pytest
import asyncio
from worker import AutoppiaWorker, WorkerRequest, WorkerResponse


class TestAutoppiaWorker:
    """Test suite for AutoppiaWorker"""
    
    @pytest.fixture
    def worker_config(self):
        """Fixture for worker configuration"""
        return {
            "model": "gpt-4",
            "max_tokens": 1000,
            "temperature": 0.7
        }
    
    @pytest.fixture
    def worker(self, worker_config):
        """Fixture for worker instance"""
        return AutoppiaWorker(config=worker_config)
    
    @pytest.mark.asyncio
    async def test_worker_initialization(self, worker):
        """Test worker initialization"""
        assert worker is not None
        assert worker.worker_name == "autoppia-miner"
        assert worker.config.model == "gpt-4"
    
    @pytest.mark.asyncio
    async def test_mine_task(self, worker):
        """Test mine task processing"""
        request = WorkerRequest(
            task="mine",
            input_data={
                "source": "test_source",
                "pattern": "test_pattern"
            }
        )
        
        response = await worker.process(request)
        
        assert response.success is True
        assert response.result is not None
        assert "mined_data" in response.result
        assert response.result["source"] == "test_source"
    
    @pytest.mark.asyncio
    async def test_process_task(self, worker):
        """Test process task"""
        request = WorkerRequest(
            task="process",
            input_data={
                "data": ["item1", "item2", "item3"]
            }
        )
        
        response = await worker.process(request)
        
        assert response.success is True
        assert response.result is not None
        assert response.result["processed_count"] == 3
    
    @pytest.mark.asyncio
    async def test_generate_task(self, worker):
        """Test generate task"""
        request = WorkerRequest(
            task="generate",
            input_data={
                "prompt": "Test prompt"
            }
        )
        
        response = await worker.process(request)
        
        assert response.success is True
        assert response.result is not None
        assert "generated_text" in response.result
    
    @pytest.mark.asyncio
    async def test_unknown_task(self, worker):
        """Test handling of unknown task"""
        request = WorkerRequest(
            task="unknown_task",
            input_data={}
        )
        
        response = await worker.process(request)
        
        assert response.success is False
        assert response.error is not None
        assert "Unknown task type" in response.error
    
    @pytest.mark.asyncio
    async def test_health_check(self, worker):
        """Test health check endpoint"""
        health = await worker.health_check()
        
        assert health["status"] == "healthy"
        assert health["worker"] == "autoppia-miner"
        assert "timestamp" in health
    
    def test_get_metadata(self, worker):
        """Test metadata retrieval"""
        metadata = worker.get_metadata()
        
        assert metadata["name"] == "autoppia-miner"
        assert metadata["version"] == "0.1.0"
        assert "capabilities" in metadata
        assert metadata["privacy_preserving"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

