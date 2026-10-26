(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b62d580a2913c4c9.js","sha256":"b62d580a2913c4c9d3b8da49b9adbc4fc7162c028e80f9cb253b5737118b3bd3","count":244});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());
