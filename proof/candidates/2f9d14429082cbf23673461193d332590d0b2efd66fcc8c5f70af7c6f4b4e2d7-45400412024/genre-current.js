(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.d4d1fcc3715afc54.js","sha256":"d4d1fcc3715afc54f84bd5bf04db1fd5c7edb119dc30242c7af303fa9fc563ad","count":244});
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
