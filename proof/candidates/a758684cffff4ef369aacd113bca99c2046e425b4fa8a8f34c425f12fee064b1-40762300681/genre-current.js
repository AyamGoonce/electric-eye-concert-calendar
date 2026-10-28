(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.a8071dde0ba83e8a.js","sha256":"a8071dde0ba83e8ae9a65df26218ddcd3df4ba9f55263b85209cfb53b097aef3","count":244});
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
