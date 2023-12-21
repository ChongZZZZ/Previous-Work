package maze.collision;

import gamecore.datastructures.CellRectangle;
import gamecore.datastructures.vectors.Vector2d;

public class Collidable implements ICollidable {

	@Override
	public void Translate(Vector2d v) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public CellRectangle GetBoundary() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public boolean IsStatic() {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean IsSolid() {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean IsTrigger() {
		// TODO Auto-generated method stub
		return false;
	}

}
