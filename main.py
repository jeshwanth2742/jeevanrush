<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Dino Runner JS</title>
  <style>
    body { margin: 0; background: #fff; overflow: hidden; }
    canvas { display: block; margin: auto; background: white; }
  </style>
</head>
<body>
<canvas id="gameCanvas" width="1100" height="600"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Screen constants
const SCREEN_WIDTH = canvas.width;
const SCREEN_HEIGHT = canvas.height;

// Load images
const RUNNING = [
  new Image(), new Image()
];
RUNNING[0].src = "Assets/Dino/DinoRun1.png";
RUNNING[1].src = "Assets/Dino/DinoRun2.png";

const JUMPING = new Image();
JUMPING.src = "Assets/Dino/DinoJump.png";

const DUCKING = [
  new Image(), new Image()
];
DUCKING[0].src = "Assets/Dino/DinoDuck1.png";
DUCKING[1].src = "Assets/Dino/DinoDuck2.png";

const SMALL_CACTUS = [new Image(), new Image(), new Image()];
SMALL_CACTUS[0].src = "Assets/Cactus/SmallCactus1.png";
SMALL_CACTUS[1].src = "Assets/Cactus/SmallCactus2.png";
SMALL_CACTUS[2].src = "Assets/Cactus/SmallCactus3.png";

const LARGE_CACTUS = [new Image(), new Image(), new Image()];
LARGE_CACTUS[0].src = "Assets/Cactus/LargeCactus1.png";
LARGE_CACTUS[1].src = "Assets/Cactus/LargeCactus2.png";
LARGE_CACTUS[2].src = "Assets/Cactus/LargeCactus3.png";

const BIRD = [new Image(), new Image()];
BIRD[0].src = "Assets/Bird/Bird1.png";
BIRD[1].src = "Assets/Bird/Bird2.png";

const CLOUD = new Image();
CLOUD.src = "Assets/Other/Cloud.png";

const BG = new Image();
BG.src = "Assets/Other/Track.png";

// Classes
class Dinosaur {
  constructor() {
    this.x = 80;
    this.y = 310;
    this.yDuck = 340;
    this.jumpVel = 8.5;
    this.stepIndex = 0;

    this.ducking = false;
    this.running = true;
    this.jumping = false;

    this.image = RUNNING[0];
    this.width = 0;
    this.height = 0;
  }

  update(keys) {
    if (this.ducking) this.duck();
    else if (this.running) this.run();
    else if (this.jumping) this.jump();

    if (this.stepIndex >= 10) this.stepIndex = 0;

    if (keys["ArrowUp"] && !this.jumping) {
      this.ducking = false;
      this.running = false;
      this.jumping = true;
    } else if (keys["ArrowDown"] && !this.jumping) {
      this.ducking = true;
      this.running = false;
      this.jumping = false;
    } else if (!this.jumping && !keys["ArrowDown"]) {
      this.ducking = false;
      this.running = true;
      this.jumping = false;
    }
  }

  duck() {
    this.image = DUCKING[Math.floor(this.stepIndex / 5)];
    this.y = this.yDuck;
    this.stepIndex++;
  }

  run() {
    this.image = RUNNING[Math.floor(this.stepIndex / 5)];
    this.y = 310;
    this.stepIndex++;
  }

  jump() {
    this.image = JUMPING;
    if (this.jumping) {
      this.y -= this.jumpVel * 4;
      this.jumpVel -= 0.8;
    }
    if (this.jumpVel < -8.5) {
      this.jumping = false;
      this.jumpVel = 8.5;
    }
  }

  draw() {
    ctx.drawImage(this.image, this.x, this.y);
    this.width = this.image.width;
    this.height = this.image.height;
  }

  rect() {
    return {x: this.x, y: this.y, w: this.width, h: this.height};
  }
}

class Cloud {
  constructor() {
    this.x = SCREEN_WIDTH + Math.floor(Math.random() * 200 + 800);
    this.y = Math.floor(Math.random() * 50 + 50);
    this.width = CLOUD.width;
  }
  update() {
    this.x -= gameSpeed;
    if (this.x < -this.width) {
      this.x = SCREEN_WIDTH + Math.floor(Math.random() * 500 + 2000);
      this.y = Math.floor(Math.random() * 50 + 50);
    }
  }
  draw() {
    ctx.drawImage(CLOUD, this.x, this.y);
  }
}

class Obstacle {
  constructor(imageArray, type) {
    this.imageArray = imageArray;
    this.type = type;
    this.image = this.imageArray[this.type];
    this.x = SCREEN_WIDTH;
    this.y = 0;
    this.width = this.image.width;
    this.height = this.image.height;
  }

  update() {
    this.x -= gameSpeed;
  }

  draw() {
    ctx.drawImage(this.image, this.x, this.y);
  }

  rect() {
    return {x: this.x, y: this.y, w: this.width, h: this.height};
  }
}

class SmallCactus extends Obstacle {
  constructor() {
    super(SMALL_CACTUS, Math.floor(Math.random() * 3));
    this.y = 325;
  }
}

class LargeCactus extends Obstacle {
  constructor() {
    super(LARGE_CACTUS, Math.floor(Math.random() * 3));
    this.y = 300;
  }
}

class Bird extends Obstacle {
  constructor() {
    super(BIRD, 0);
    this.y = 250;
    this.index = 0;
  }
  draw() {
    this.image = this.imageArray[Math.floor(this.index/5)];
    ctx.drawImage(this.image, this.x, this.y);
    this.index++;
    if (this.index >= 10) this.index = 0;
  }
}

// Game variables
let gameSpeed = 20;
let xPosBg = 0;
let yPosBg = 380;
let points = 0;
let obstacles = [];
let deathCount = 0;

const player = new Dinosaur();
const cloud = new Cloud();
let keys = {};

// Input handling
document.addEventListener("keydown", e => keys[e.key] = true);
document.addEventListener("keyup", e => keys[e.key] = false);

// Collision check
function collide(rect1, rect2) {
  return rect1.x < rect2.x + rect2.w &&
         rect1.x + rect1.w > rect2.x &&
         rect1.y < rect2.y + rect2.h &&
         rect1.y + rect1.h > rect2.y;
}

// Score
function drawScore() {
  ctx.font = "20px Arial";
  ctx.fillStyle = "black";
  ctx.fillText("Points: " + points, 950, 40);

  points++;
  if (points % 100 === 0) {
    gameSpeed++;
  }
}

// Background
function drawBackground() {
  const imageWidth = BG.width;
  ctx.drawImage(BG, xPosBg, yPosBg);
  ctx.drawImage(BG, imageWidth + xPosBg, yPosBg);
  if (xPosBg <= -imageWidth) {
    xPosBg = 0;
  }
  xPosBg -= gameSpeed;
}

// Main game loop
function gameLoop() {
  ctx.clearRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
  ctx.fillStyle = "white";
  ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

  player.update(keys);
  player.draw();

  if (obstacles.length === 0) {
    let choice = Math.floor(Math.random() * 3);
    if (choice === 0) obstacles.push(new SmallCactus());
    else if (choice === 1) obstacles.push(new LargeCactus());
    else obstacles.push(new Bird());
  }

  for (let i = 0; i < obstacles.length; i++) {
    obstacles[i].update();
    obstacles[i].draw();

    if (collide(player.rect(), obstacles[i].rect())) {
      alert("Game Over! Score: " + points);
      document.location.reload();
    }

    if (obstacles[i].x < -obstacles[i].width) {
      obstacles.splice(i, 1);
    }
  }

  cloud.update();
  cloud.draw();

  drawBackground();
  drawScore();

  requestAnimationFrame(gameLoop);
}

// Start the game
gameLoop();

</script>
</body>
</html>
