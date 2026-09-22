(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a8e51c04473fdcdf.js","sha256":"a8e51c04473fdcdf6aec37723adb80f3989bf1275fb4018cba6ccd3636de9fc2","count":2130,"publishedAt":"2026-09-22T11:31:40Z","state":"calendar-state.json","stateSha256":"949a322d7cb37412e6353c17cda43720daa1229d6a765995c31c021053dcd936","sourceState":"calendar-source-state.json","sourceStateSha256":"c333e40e0b07327ce54d539476cdd4ef47f297c1feb7213d146faba7514677b0"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
