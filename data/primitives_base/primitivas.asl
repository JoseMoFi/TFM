+!move_to(Site) : accessible(Site) <- 
    .print("Moviendo a ", Site);
    .move(Site);
    -+at(Site).

+!catch_object(Object) : at(Here) & has(Object, Count) & object_at(Object, Here)<- 
    NewCount = Count + 1;
    .print("Cogiendo ", Object, " → inventario: ", NewCount);
    .catch(Object);
    .update_inventory(Object, 1, "add").

+!drop_object(Object) : at(Site) & has(Object, Count)<- 
    NewCount = Count - 1;
    .print("Soltando ", Object, " en ", Site, " → inventario: ", NewCount);
    .update_inventory(Object, 1, "subtract");
    .drop(Object, Site).

+!search_object(Object) : true <-
    .search(Object).