(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.d43ca88581b060ec.js","sha256":"d43ca88581b060ec7bd3ebfc679af8dace6e91c84a256f398999d5f280f40838","count":244});
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
