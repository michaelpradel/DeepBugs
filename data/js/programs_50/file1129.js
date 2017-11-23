define([
        'lodash',
        'math/vector2',
        'math/vector3',
        'core/controller',
        'graphics/meshFactory',
        'graphics/mesh',
        'components/quad'
    ], 
    function(
        _,
        Vector2,
        Vector3,
        Controller,
        MeshFactory,
        Mesh,
        Quad
    ) {
        'use strict';

        /**
        *   This class updates the mesh associated with entities which have a
        *   Quad component.
        *
        *   @class 
        *   @param {context}
        *   @constructor
        */
        var QuadController = function(context) {
            Controller.call(this, context);

            this.meshFactory = new MeshFactory(this.device);
        };

        QuadController.prototype = _.create(Controller.prototype, {
            constructor: QuadController,

            /**
            *   Update all entities which contain the Quad and MeshFilter
            *   components.
            *
            *   @method update
            *   @returns {undefined}
            */
            update: function() {
                this.filterBy(['Transform', 'Quad', 'Dimensions', 'MeshFilter'], function(entity) {
                    var quad       = entity.getComponent('Quad');
                    var dimensions = entity.getComponent('Dimensions');

                    if (quad.isDirty() || dimensions.isDirty()) {
                        var meshFilter = entity.getComponent('MeshFilter');
                        var mesh       = meshFilter.getMesh();

                        if (mesh) {
                            mesh.destroy();
                        } else {
                            mesh = new Mesh(this.device, Mesh.TRIANGLES);
                        }

                        this.generateQuadMesh(entity, mesh);
                        meshFilter.setMesh(mesh);

                        quad.setDirty(false);
                    }
                }, this);
            },

            /**
            *   Generate the 6 faces of a quad and return a mesh.
            *
            *   @method generateQuadMesh
            *   @param {entity}
            *   @param {mesh}
            *   @returns {mesh}
            */
            generateQuadMesh: function(entity, mesh) {
                var quad       = entity.getComponent('Quad');
                var dimensions = entity.getComponent('Dimensions');

                var w, h, hw, hh;

                w = dimensions.getWidth();
                h = dimensions.getHeight();

                hw = w / 2;
                hh = h / 2;

                this.meshFactory.begin(mesh);

                this.generateFace(hw, hh, quad);

                this.meshFactory.end();

                return mesh;
            },

            /**
            *   Generate the quad face.
            *
            *   @method generateFace
            *   @param {w} width
            *   @param {h} height
            *   @param {quad} quad
            *   @returns {undefined}
            */
            generateFace: function(w, h, quad) {
                var sprite = quad.sprite;

                var vertexCount = this.meshFactory.getVertexCount();

                if (sprite) {
                    var u, v, s, t;
                    u = sprite.getUCoordinate();
                    v = sprite.getVCoordinate();
                    s = sprite.getUVWidth();
                    t = sprite.getUVHeight();

                    this.meshFactory.addUVtoLayer0(new Vector2(u + 0, v + t));
                    this.meshFactory.addUVtoLayer0(new Vector2(u + 0, v + 0));
                    this.meshFactory.addUVtoLayer0(new Vector2(u + s, v + 0));
                    this.meshFactory.addUVtoLayer0(new Vector2(u + s, v + t));
                }

                this.meshFactory.addVertex(new Vector3(-w, -h, 0));
                this.meshFactory.addVertex(new Vector3(-w,  h, 0));
                this.meshFactory.addVertex(new Vector3( w,  h, 0));
                this.meshFactory.addVertex(new Vector3( w, -h, 0));

                this.meshFactory.addTriangle(vertexCount, vertexCount + 2, vertexCount + 1);
                this.meshFactory.addTriangle(vertexCount, vertexCount + 3, vertexCount + 2);
            }
        });

        return QuadController;
    }
);
