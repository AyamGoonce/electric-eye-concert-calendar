(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.9953d39b3de283da.js","sha256":"9953d39b3de283da47aff591f2ce20215f2d113901da34b2630d6b068f44d5aa","count":248});
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
