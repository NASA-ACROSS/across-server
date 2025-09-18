# merge.jq - run with: jq -s -f merge.jq s3_task_def.json incoming_taskdef.json

# Turn a taskdef's containerDefinitions array into an object keyed by container name
def to_obj($td):
  ($td.containerDefinitions // []) as $cd
  | reduce $cd[] as $c ({}; .[$c.name] = $c);

# Merge two container objects $b (base) and $o (override) for a single container name
def merge_one($b; $o):
  ($b // {}) as $base
  | ($o // {}) as $over
  | ($base * $over) as $shallow_merged
  | if ($base.environment? or $over.environment?) then
      $shallow_merged
      | .environment = (
          (($base.environment // []) + ($over.environment // []))
          | sort_by(.name)                 # required before group_by
          | group_by(.name)
          | map(.[-1])                     # last occurrence wins (override)
        )
    else
      $shallow_merged
    end;

# Main pipeline
. as $inputs
| $inputs[0] as $s3
| $inputs[1] as $incoming

# objects keyed by container name
| to_obj($s3) as $base_containers
| to_obj($incoming) as $over_containers

# all container names (union)
| (($base_containers | keys) + ($over_containers | keys) | unique) as $all_names

# build merged containers map (note parentheses around reduce)
| (reduce $all_names[] as $name ({}; .[$name] = merge_one($base_containers[$name]; $over_containers[$name]))) as $merged_map

# produce final merged task def: top-level merge, but use merged containerDefinitions
| ($s3 + $incoming) | .containerDefinitions = ($merged_map | to_entries | map(.value))
