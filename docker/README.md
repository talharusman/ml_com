# Docker-based Sandboxing for F1-Score Grand Prix

For production environments, use Docker to provide stronger isolation for user submissions.

## Build the Docker Image

\`\`\`bash
docker build -f docker/runner.Dockerfile -t ml-competition-runner .
\`\`\`

## Run a Submission in Docker

\`\`\`bash
docker run \
  --rm \
  --memory=512m \
  --cpus=1 \
  --network=none \
  --read-only \
  -v $(pwd)/backend/data:/data:ro \
  -v $(pwd)/backend/submissions:/submissions:ro \
  ml-competition-runner \
  python3 /submissions/task1_<submission_id>.py --run --train /data/task1_train.csv --test /data/task1_test.csv --out /tmp/predictions.csv
\`\`\`

## Security Features

- **Memory limit**: 512 MB (`--memory=512m`)
- **CPU limit**: 1 core (`--cpus=1`)
- **No network**: `--network=none`
- **Read-only filesystem**: `--read-only`
- **Mounted volumes as read-only**: `:ro`

## Integration with Backend

To use Docker for evaluation instead of subprocess:

1. Update `backend/evaluator.py` to use Docker commands
2. Ensure Docker daemon is running
3. Adjust container resources as needed

Example modification:

\`\`\`python
import subprocess

def safe_run_submission_docker(script_path, args, timeout=120):
    cmd = [
        'docker', 'run',
        '--rm',
        '--memory=512m',
        '--cpus=1',
        '--network=none',
        f'-v {script_path.parent}:/submissions:ro',
        'ml-competition-runner',
        'python3', f'/submissions/{script_path.name}', *args
    ]
    
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
\`\`\`

## Notes

- Ensure Docker is installed: `docker --version`
- Build image before running containers
- Adjust memory/CPU limits based on your hardware
