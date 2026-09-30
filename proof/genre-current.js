(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.850a20ad8ae8ac08.js","sha256":"850a20ad8ae8ac0863119be992b2daa99acb5abb860f5942e34a179ce567cea3","count":207});
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
