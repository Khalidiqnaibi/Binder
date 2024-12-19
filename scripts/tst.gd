extends CharacterBody2D

const SPEED = 300.0
const JUMP_VELOCITY = -400.0
const ROLL_SPEED = 400.0
const CROUCH_SPEED = 150.0

var is_crouching = false
var is_rolling = false
var is_jmping= false

func anime(anime_name:String):
	$AnimatedSprite2D.play(anime_name)
	#await $AnimatedSprite2D.animation_finished
	#if is_on_floor():
	#	$AnimatedSprite2D.play("default")

func _ready():

	# Ensure the default shape is active initially
	anime("default")
	
	set_collision_shape("normal")

func _physics_process(delta: float) -> void:
	# Add gravity if not on the floor
	if not is_on_floor():
		velocity.y += get_gravity().y * delta
	else:
		is_jmping = false

	# Handle jump
	if Input.is_action_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY
		is_jmping =true

	# Handle combat roll
	if Input.is_action_just_pressed("roll") and not is_rolling:
		anime("attk")
		do_combat_roll()

	# Handle crouch
	if Input.is_action_pressed("crouch"):
		start_crouching()
	else:
		stop_crouching()

	# Movement direction
	var direction = Input.get_axis("left", "right")

	# Adjust speed for crouching
	var current_speed = SPEED
	if is_crouching:
		current_speed = CROUCH_SPEED

	# Apply horizontal movement
	if direction:
		velocity.x = direction * current_speed
		anime("run")
	else:
		#anime("default")
		
		velocity.x = move_toward(velocity.x, 0, SPEED)
	
	# Perform movement
	move_and_slide()
	
	if is_jmping and not is_on_floor() :
		anime("jump")
		#await $AnimatedSprite2D.animation_finished
		#$AnimatedSprite2D.play("default")
	else:
		is_jmping =false

func do_combat_roll() -> void:
	# Start the roll
	is_rolling = true
	set_collision_shape("roll")  # Switch to the roll shape
	velocity.x = ROLL_SPEED * sign(velocity.x)
	await get_tree().create_timer(0.5).timeout  # Duration of the roll
	print('roll')
	is_rolling = false
	set_collision_shape("normal")  # Switch back to default

func start_crouching() -> void:
	if not is_crouching:
		is_crouching = true
		set_collision_shape("crouch")  # Switch to the crouch shape

func stop_crouching() -> void:
	if is_crouching and not Input.is_action_pressed("crouch"):
		is_crouching = false
		set_collision_shape("normal")  # Switch back to default

func set_collision_shape(state: String) -> void:
	if $normal and $roll:
		for child in [$normal,$roll]:
			child.disabled = true
		if state == "normal":
			$normal.disabled = false
		elif state == "roll":
			$roll.disabled = false
		elif state == "crouch":
			$roll.disabled = false
