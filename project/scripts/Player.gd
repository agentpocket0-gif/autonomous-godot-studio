extends CharacterBody3D

@export var forward_speed: float = 12.0
@export var lane_width: float = 2.5
@export var jump_velocity: float = 8.0
var gravity: float = 20.0
var current_lane: int = 0

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity * delta

	velocity.z = -forward_speed
	var target_x = current_lane * lane_width
	velocity.x = (target_x - global_position.x) * 15.0

	move_and_slide()
